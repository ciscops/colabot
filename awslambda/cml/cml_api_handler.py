import logging
import os
import sys
import tempfile
from datetime import datetime, timedelta
import json
import traceback
import yaml
import boto3
from requests.exceptions import HTTPError
from virl2_client import ClientLibrary
from webexteamssdk import WebexTeamsAPI
from awslambda.cml.dynamo_api_handler import Dynamoapi


class CMLAPI:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
        self.logging = logging.getLogger()

        try:
            self.CML_MAX_NODE_COUNT = int(os.environ["CML_MAX_NODE_COUNT"]) - int(
                os.environ["CML_MAX_NODE_COUNT_CUSHION"]
            )
            self.CML_USERNAME = os.environ["CML_USERNAME"]
            self.CML_PASSWORD = os.environ["CML_PASSWORD"]
            self.LONG_LIVED_LABS = os.environ["LONG_LIVED_LABS_GROUP"]
            self.DELETE_DAYS = int(os.environ["LAB_DELETE_DAYS"])
            self.DELETE_LABS_CRON_JOB_NAME = os.environ["DELETE_LABS_CRON_JOB_NAME"]
            self.DELETE_LABS_CRON_JOB_ID = os.environ["DELETE_LABS_CRON_JOB_ID"]
            self.DELETE_LABS_CRON_JOB_ARN = os.environ["DELETE_LABS_CRON_JOB_ARN"]
            self.ADMIN_WEBEX_ROOM_ID = os.environ["ADMIN_WEBEX_ROOM_ID"]
            self.DELETE_LABS_CRON_JOB_WAIT_TIME = int(
                os.environ["DELETE_LABS_CRON_JOB_WAIT_TIME"]
            )
            self.ARN = os.environ["SELF_ARN"]
            self.CML_URL = os.environ["CML_URL"]
        except KeyError as e:
            logging.error("Environment variable %s must be set", str(e))
            sys.exit(1)

        self.eventbridge_client = boto3.client("events")
        self.lambda_client = boto3.client("lambda")
        self.cml_client = None
        self.webex_api = WebexTeamsAPI()
        self.dynamodb = Dynamoapi()
        self.user_and_labs = {}
        self.long_lived_users = []
        self.CREATED_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S+00:00"
        self.NODES_NOT_COUNT_LICENSE = [
            "trex",
            "wan_emulator",
            "alpine",
            "desktop",
            "server",
            "ubuntu",
            "coreos",
            "external_connector",
            "unmanaged_switch",
        ]
        self.NODE_LICENSE_ERROR = """{
  "description": "Licensing issue: Maximum node count exceeded.",
  "code": 400
}"""

    def connect(self):
        """starts connection to cml api if there is none"""
        if self.cml_client is None:
            self.cml_client = ClientLibrary(
                self.CML_URL,
                self.CML_USERNAME,
                self.CML_PASSWORD,
                ssl_verify=False,
                raise_for_auth_failure=True,
            )
        self.logging.info("CONNECTED")

    def fill_user_labs_dict(self) -> dict:
        """gets all user emails and labs from cml as well as seeing if user in long lived labs group"""
        self.connect()
        self.logging.info("Getting diagnostics")
        diagnostics = self.cml_client.get_diagnostics()

        self.logging.debug("Iterating through users")
        for user in diagnostics["user_list"]:
            email = user["username"] + "@cisco.com"
            self.user_and_labs[email] = user["labs"]

            if self.LONG_LIVED_LABS in user["groups"]:
                self.long_lived_users.append(email)

    def user_in_long_lived_labs(self, email: str) -> bool:
        """Checks if user is in the long lived labs group"""
        self.connect()
        if email in self.long_lived_users:
            return True
        return False

    def get_user_labs(self, email: str) -> dict:
        """
        Returns a dictionary of the user's labs

        return: {id: (title, date_created)}
        """
        self.connect()
        labs = {}

        try:
            user_labs = self.user_and_labs[email]
        except KeyError:
            self.logging.info("User %s does not have any labs", email)
            return {}

        for lab_id in user_labs:
            lab = self.cml_client.join_existing_lab(lab_id)
            details = lab.details()

            # check if in long lived labs:
            is_long_living = False
            groups = details["groups"]
            for group in groups:
                if group["id"] == self.LONG_LIVED_LABS:
                    is_long_living = True
                    break

            # if not long living, get all labs
            if not is_long_living:
                lab_id = details["id"]
                title = details["lab_title"]
                created_date = datetime.strptime(
                    details["created"], self.CREATED_DATE_FORMAT
                )
                labs[lab_id] = {"title": title, "created_date": created_date}

        return labs

    def stop_labs(self, labs_to_stop: list, email: str) -> bool:
        """Stops the labs and messages the user"""

        if not labs_to_stop:
            return False

        self.connect()
        for lab_dict in labs_to_stop:
            try:
                lab_id = lab_dict["lab_id"]
                reason_lab_stopped = lab_dict["reason_lab_stopped"]

                lab = self.cml_client.join_existing_lab(lab_id)

                lab.stop(wait=False)
                self.logging.info("Stopped lab %s", lab.title)
                self.dynamodb.update_cml_lab_stopped(email, lab_id)

                lab_title = lab.title
                message = (
                    "Lab: **"
                    + lab_title
                    + f"**\n - Status: **Stopped** \n - Reason: {reason_lab_stopped}"
                )
                self.webex_api.messages.create(toPersonEmail=email, markdown=message)
            except Exception as e:
                self.send_admin_error_message(lab=lab_id)
                self.logging.error("Error stopping lab: %s", str(e))

        return True

    def start_delete_process(self, labs_to_delete: dict) -> bool:
        """Tries to start all the labs and enables the EventBridge Cron Job"""
        self.connect()

        self.logging.info("Start deleting labs")

        # get number nodes started
        base_number_nodes_started = self.get_number_nodes_active()
        self.logging.info("Base Started Nodes: %d", base_number_nodes_started)
        self.check_able_delete_labs(base_number_nodes_started, labs_to_delete)

        number_program_started_nodes = 0

        # Try to start all labs
        started_labs = []
        stopped_labs = []
        self.logging.info("Starting labs")
        max_node_limit_reached = False
        for lab_data in labs_to_delete:
            try:
                lab_id = lab_data["lab_id"]
                user_email = lab_data["user_email"]

                lab = self.cml_client.join_existing_lab(lab_id)
                lab_title = lab.title
                self.logging.info("Title: %s", lab_title)

                # check to see if lab is running - if it is, reset lifecycle
                self.logging.info("Check if lab is started")
                if lab.state() == "STARTED":
                    self.logging.info(
                        "Lab %s in started state - resetting in dynamo", lab_title
                    )
                    self.dynamodb.update_cml_lab_used_date(
                        user_email, lab_id, lab_title
                    )
                    continue

                # if node limit reached, put all other labs as stopped
                if max_node_limit_reached:
                    stopped_labs.append(lab_data)
                    continue

                # try and start as many nodes as possible
                max_node_limit_reached, nodes = self.start_lab_nodes(
                    lab, base_number_nodes_started, number_program_started_nodes
                )

                lab_data["nodes"] = nodes
                started_labs.append(lab_data)
            except Exception as e:
                self.send_admin_error_message(lab=lab_id)
                self.logging.error("Error deleting lab %s: %s", lab_title, str(e))

        # if more labs to delete, start the cron job
        if len(started_labs) != 0:
            self.start_delete_labs_cron_job(
                started_labs, stopped_labs, number_program_started_nodes
            )

        return True

    def check_lab_converged(self, event: dict) -> bool:
        """Checks if labs have started and deletes them"""

        self.logging.info("Check Labs Converge")

        self.disable_delete_labs_cron_job()
        self.connect()

        started_labs = event["started_labs"]
        stopped_labs = event["stopped_labs"]
        number_program_started_nodes = event["number_program_started_nodes"]

        # automatically assume node limit reached is true
        max_node_limit_reached = True

        for lab_data in started_labs.copy():
            try:
                lab_id = lab_data["lab_id"]
                user_email = lab_data["user_email"]
                nodes = lab_data["nodes"]

                lab = self.cml_client.join_existing_lab(lab_id)
                lab_title = lab.title

                self.logging.info("Checking if converged %s", lab_title)

                # check all nodes, see if converged, and if so  extract configuration
                self.check_lab_nodes_converged(
                    lab,
                    nodes,
                    started_labs,
                    stopped_labs,
                    number_program_started_nodes,
                    max_node_limit_reached,
                )

                # only reassess nodes and such after the delay and not after each recursion
                # note: this entire section was in the beginning of fx, but since restart lambda call after each config extraction, didn't want to waste time
                self.fill_user_labs_dict()

                base_number_nodes_started = (
                    self.get_number_nodes_active() - number_program_started_nodes
                )

                self.check_able_delete_labs(
                    base_number_nodes_started, started_labs + stopped_labs
                )

                # if limit_reached is true, means no nodes converged. But test to make sure actually true
                # if false, means a node converged and was stopped, so we know we can start a node
                if max_node_limit_reached:
                    max_node_limit_reached = (
                        base_number_nodes_started + number_program_started_nodes
                        >= self.CML_MAX_NODE_COUNT
                    )

                if max_node_limit_reached:
                    continue

                # start as many stopped nodes in this lab
                max_node_limit_reached = self.start_stopped_lab_nodes(
                    lab, nodes, base_number_nodes_started, number_program_started_nodes
                )

                # no more stopped nodes and no started nodes, so can download and delete lab
                if not nodes["stopped"] and not nodes["started"]["all"]:
                    yaml_string = lab.download()

                    lab.stop()
                    lab.wipe()
                    lab.remove()
                    self.send_lab_topology(yaml_string, lab_title, user_email)
                    self.dynamodb.delete_cml_lab(user_email, lab.id)
                    started_labs.remove(lab_data)

            except Exception as e:
                self.send_admin_error_message(lab=lab_id)
                self.logging.error("Error deleting lab %s: %s", lab_title, str(e))

        # try and start a non-started lab
        if not max_node_limit_reached:
            for lab_data in stopped_labs.copy():
                lab_id = lab_data["lab_id"]
                user_email = lab_data["user_email"]

                lab = self.cml_client.join_existing_lab(lab_id)
                lab_title = lab.title

                # try and start as many nodes as possible
                max_node_limit_reached, nodes = self.start_lab_nodes(
                    lab, base_number_nodes_started, number_program_started_nodes
                )

                lab_data["nodes"] = nodes
                started_labs.append(lab_data)
                stopped_labs.remove(lab_data)

                if max_node_limit_reached:
                    break

        # if more labs to delete, start the cron job
        if len(started_labs) != 0:
            self.start_delete_labs_cron_job(
                started_labs, stopped_labs, number_program_started_nodes
            )

        else:
            self.logging.info("DONE DELETING LABS")

        return True

    def start_delete_labs_cron_job(
        self, started_labs: list, stopped_labs: list, number_program_started_nodes: int
    ) -> bool:
        """Enables the delete labs cron job"""

        # update schedule
        t = datetime.now() + timedelta(minutes=self.DELETE_LABS_CRON_JOB_WAIT_TIME)

        self.eventbridge_client.put_rule(
            Name=self.DELETE_LABS_CRON_JOB_NAME,
            ScheduleExpression=f"cron({t.minute} {t.hour} {t.day} {t.month} ? {t.year})",
        )

        # update target json info with lab data
        event = self.get_cron_job_payload(
            started_labs, stopped_labs, number_program_started_nodes
        )
        event["is_cron_job_delay"] = True

        self.eventbridge_client.put_targets(
            Rule=self.DELETE_LABS_CRON_JOB_NAME,
            Targets=[
                {
                    "Id": self.DELETE_LABS_CRON_JOB_ID,
                    "Arn": self.DELETE_LABS_CRON_JOB_ARN,
                    "Input": json.dumps(event),
                }
            ],
        )

        self.eventbridge_client.enable_rule(Name=self.DELETE_LABS_CRON_JOB_NAME)

        return True

    def get_cron_job_payload(
        self, started_labs: list, stopped_labs: list, number_program_started_nodes: int
    ) -> dict:
        """Returns the necessary payload to continue deleting labs"""

        event = {
            "type": "continue_cron_job",
            "number_program_started_nodes": number_program_started_nodes,
            "started_labs": started_labs,
            "stopped_labs": stopped_labs,
        }
        return event

    def disable_delete_labs_cron_job(self) -> bool:
        """Disables cron job and puts null target data"""
        self.eventbridge_client.put_targets(
            Rule=self.DELETE_LABS_CRON_JOB_NAME,
            Targets=[
                {
                    "Id": self.DELETE_LABS_CRON_JOB_ID,
                    "Arn": self.DELETE_LABS_CRON_JOB_ARN,
                    "Input": "",
                }
            ],
        )

        self.eventbridge_client.disable_rule(Name=self.DELETE_LABS_CRON_JOB_NAME)

        return True

    def send_lab_topology(self, yaml_string: str, lab_title: str, email: str) -> bool:
        """Downloads the lab and sends it to the user"""
        self.logging.info("Sending Topology file to user")

        with open(
            tempfile.NamedTemporaryFile(
                suffix=".yaml", prefix=f'{lab_title.replace(" ","_")}_'
            ).name,
            "w",
            encoding="utf-8",
        ) as outfile:
            yaml.dump(yaml.full_load(yaml_string), outfile, default_flow_style=False)

            self.webex_api.messages.create(
                toPersonEmail=email,
                markdown="Lab: **"
                + lab_title
                + f"**\n - Status: **Deleted** \n - Reason: Exceeded {self.DELETE_DAYS} day stopped timeframe",
                files=[outfile.name],
            )

        return True

    def check_lab_active(self, lab_id: str) -> bool:
        """Returns whether a lab is active or not"""
        lab = self.cml_client.join_existing_lab(lab_id)
        return lab.state() == "STARTED"

    def get_number_nodes_active(self) -> int:
        """Returns the number of active nodes"""
        number_of_active_nodes = 0
        for user_labs in self.user_and_labs.values():
            for lab_id in user_labs:
                lab = self.cml_client.join_existing_lab(lab_id)
                for node in lab.nodes():
                    if (
                        node.is_active()
                        and node.node_definition not in self.NODES_NOT_COUNT_LICENSE
                    ):
                        number_of_active_nodes += 1

        return number_of_active_nodes

    def start_lab_nodes(
        self,
        lab,
        base_number_nodes_started: int,
        number_program_started_nodes: int,
        max_node_limit_reached: bool = False,
    ) -> tuple:
        """Try and start as many nodes as possible in a lab.

        Returns: (bool, dict)
        """

        nodes = {"started": {"all": [], "no_license": []}, "stopped": []}

        for node in lab.nodes():
            try:
                # don't count towards max node count
                if node.node_definition in self.NODES_NOT_COUNT_LICENSE:
                    node.start(wait=False)
                    nodes["started"]["no_license"].append(node.id)
                    nodes["started"]["all"].append(node.id)

                elif (
                    base_number_nodes_started + number_program_started_nodes + 1
                    <= self.CML_MAX_NODE_COUNT
                ):
                    node.start(wait=False)
                    nodes["started"]["all"].append(node.id)
                    number_program_started_nodes += 1

                # means reached limit
                else:
                    max_node_limit_reached = True
                    nodes["stopped"].append(node.id)
            except HTTPError as e:
                self.send_admin_error_message()
                if e.response.text == self.NODE_LICENSE_ERROR:
                    max_node_limit_reached = True
                    nodes["stopped"].append(node.id)

        return max_node_limit_reached, nodes

    def start_stopped_lab_nodes(
        self,
        lab,
        nodes: dict,
        base_number_nodes_started: int,
        number_program_started_nodes: int,
        max_node_limit_reached: bool = False,
    ) -> bool:
        for node_id in nodes["stopped"].copy():
            try:
                if (
                    base_number_nodes_started + number_program_started_nodes + 1
                    <= self.CML_MAX_NODE_COUNT
                ):
                    self.logging.info("Adding node from stopped")
                    node = lab.get_node_by_id(node_id)
                    node.start(wait=False)
                    nodes["started"]["all"].append(node_id)
                    nodes["stopped"].remove(node_id)
                    number_program_started_nodes += 1

                # only add started_nodes if not all nodes started
                else:
                    max_node_limit_reached = True
                    break
            except HTTPError as e:
                self.send_admin_error_message(lab=lab.id)
                if e.response.text == self.NODE_LICENSE_ERROR:
                    max_node_limit_reached = True
                    break

        return max_node_limit_reached

    def check_lab_nodes_converged(
        self,
        lab,
        nodes: dict,
        started_labs: dict,
        stopped_labs: dict,
        number_program_started_nodes: int,
        max_node_limit_reached=True,
    ) -> bool:
        """Checks to see if nodes have converged, and if so, extracts their configs"""

        for node_id in nodes["started"]["all"].copy():
            node = lab.get_node_by_id(node_id)
            if node.has_converged():
                # fetch config from device - exception because certain nodes don't allow extraction
                self.logging.info("Update configs for node")
                try:
                    # Make sure won't go out of AWS TIMEOUT
                    node.extract_configuration()
                except Exception as e:
                    self.logging.error("ERROR extracting node config: %s", str(e))
                node.stop(wait=True)
                nodes["started"]["all"].remove(node_id)

                if node_id in nodes["started"]["no_license"]:
                    nodes["started"]["no_license"].remove(node_id)
                    continue

                number_program_started_nodes -= 1
                max_node_limit_reached = False

                ## instant recall of lambda to make sure don't timeout since some node extractions take a while
                event = self.get_cron_job_payload(
                    started_labs, stopped_labs, number_program_started_nodes
                )
                self.lambda_client.invoke(
                    FunctionName=self.ARN,
                    InvocationType="Event",
                    LogType="Tail",
                    Payload=json.dumps(event),
                )
                sys.exit(0)

        return max_node_limit_reached

    def check_able_delete_labs(self, base_number_nodes_running, all_labs) -> bool:
        """If too many base nodes are started, exits function and notifies admins"""

        if base_number_nodes_running < self.CML_MAX_NODE_COUNT:
            return True

        self.logging.warning(
            "Unable to delete labs due to too many nodes started - exiting program and sending message to admin"
        )
        self.connect()

        message = "**WARNING** The following labs were unable to be deleted due to too many nodes started: "
        for lab_data in all_labs:
            lab_id = lab_data["lab_id"]
            message += f"\n- Lab Id: {lab_id}"
            if "nodes" in lab_data:
                lab = self.cml_client.join_existing_lab(lab_id)
                lab.stop(wait=False)

        self.webex_api.messages.create(
            roomId=self.ADMIN_WEBEX_ROOM_ID, markdown=message
        )

        sys.exit(1)

    def send_admin_error_message(self, lab: str = None) -> bool:
        """Sends the error message to the webex admin room"""
        # TODO: Stop all labs if critical

        if lab:
            message = f"The following lab encoutered an error while running CML Manage Labs: \nLab {lab}\n\n <pre>{traceback.format_exc()}</code></pre>"
        else:
            message = f"An error was encoutered while running CML Manage Labs: <pre>{traceback.format_exc()}</code></pre>"

        self.webex_api.messages.create(
            roomId=self.ADMIN_WEBEX_ROOM_ID, markdown=message
        )

        try:
            self.connect()
            cml_lab = self.cml_client.join_existing_lab(lab)
            cml_lab.stop(wait=False)
        except Exception:
            pass

        return True
