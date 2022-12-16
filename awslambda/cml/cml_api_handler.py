import logging
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta
import json
import traceback
import yaml
import boto3
from requests.exceptions import HTTPError
from virl2_client import ClientLibrary
from webexteamssdk import WebexTeamsAPI
from awslambda.cml.dynamo_api_handler import Dynamoapi

# TODO: what if cron job takes 24 hours - would sense stopped labs as started and re put back into start of system


class CMLAPI:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
        self.logging = logging.getLogger()

        if "CML_USERNAME" not in os.environ:
            logging.error("Environment variable CML_USERNAME must be set")
            sys.exit(1)

        if "CML_PASSWORD" not in os.environ:
            logging.error("Environment variable CML_PASSWORD must be set")
            sys.exit(1)

        if "LONG_LIVED_LABS_GROUP" not in os.environ:
            logging.error("Environment variable LONG_LIVED_LABS_GROUP must be set")
            sys.exit(1)

        if "STOPPED_LABS_GROUP" not in os.environ:
            logging.error("Environment variable STOPPED_LABS_GROUP must be set")
            sys.exit(1)

        if "LAB_DELETE_DAYS" not in os.environ:
            logging.error("Environment variable LAB_DELETE_DAYS must be set")
            sys.exit(1)

        if "DELETE_LABS_CRON_JOB_NAME" not in os.environ:
            logging.error("Environment variable DELETE_LABS_CRON_JOB_NAME must be set")
            sys.exit(1)

        if "DELETE_LABS_CRON_JOB_ID" not in os.environ:
            logging.error("Environment variable DELETE_LABS_CRON_JOB_ID must be set")
            sys.exit(1)

        if "DELETE_LABS_CRON_JOB_ARN" not in os.environ:
            logging.error("Environment variable DELETE_LABS_CRON_JOB_ARN must be set")
            sys.exit(1)

        if "CML_MAX_NODE_COUNT" not in os.environ:
            logging.error("Environment variable CML_MAX_NODE_COUNT must be set")
            sys.exit(1)

        if "CML_MAX_NODE_COUNT_CUSHION" not in os.environ:
            logging.error("Environment variable CML_MAX_NODE_COUNT_CUSHION must be set")
            sys.exit(1)

        if "ADMIN_WEBEX_ROOM_ID" not in os.environ:
            logging.error("Environment variable ADMIN_WEBEX_ROOM_ID must be set")
            sys.exit(1)

        self.cml_max_node_count = int(os.getenv("CML_MAX_NODE_COUNT")) - int(
            os.getenv("CML_MAX_NODE_COUNT_CUSHION")
        )
        self.logging.info("MAX NODE COUNT: %d", self.cml_max_node_count)
        self.cml_username = os.getenv("CML_USERNAME")
        self.cml_password = os.getenv("CML_PASSWORD")
        self.long_lived_labs = os.getenv("LONG_LIVED_LABS_GROUP")
        self.stopped_labs_group = os.getenv("STOPPED_LABS_GROUP")
        self.DELETE_DAYS = int(os.getenv("LAB_DELETE_DAYS"))
        self.delete_labs_cron_job_name = os.getenv("DELETE_LABS_CRON_JOB_NAME")
        self.delete_labs_cron_job_id = os.getenv("DELETE_LABS_CRON_JOB_ID")
        self.delete_labs_cron_job_arn = os.getenv("DELETE_LABS_CRON_JOB_ARN")
        self.admin_webex_room_id = os.getenv("ADMIN_WEBEX_ROOM_ID")

        self.eventbridge_client = boto3.client("events")
        self.eventbridge_scheduler = boto3.client("scheduler")
        self.cml_client = None
        self.webex_api = WebexTeamsAPI()
        self.dynamodb = Dynamoapi()
        self.created_date_format = "%Y-%m-%dT%H:%M:%S+00:00"
        self.user_and_labs = {}
        self.long_lived_users = []
        self.nodes_not_count_license = [
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
        self.node_license_error = """{
  "description": "Licensing issue: Maximum node count exceeded.",
  "code": 400
}"""
        self.MAX_AWS_TIME = 870000

    def connect(self):
        """starts connection to cml api if there is none"""
        if self.cml_client is None:
            url = "https://cpn-rtp-cml-stable1.ciscops.net/"
            self.cml_client = ClientLibrary(
                url,
                self.cml_username,
                self.cml_password,
                ssl_verify=False,
                raise_for_auth_failure=True,
            )
        self.logging.info("CONNECTED")

    def fill_user_labs_dict(self) -> dict:
        """gets all user emails and labs from cml as well as seeing if user in long lived labs group"""
        self.connect()
        self.logging.info("Getting diagnostics")
        diagnostics = self.cml_client.get_diagnostics()

        self.logging.debug("iterating through users")
        for user in diagnostics["user_list"]:
            email = user["username"] + "@cisco.com"
            self.user_and_labs[email] = user["labs"]

            if self.long_lived_labs in user["groups"]:
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
                if group["id"] == self.long_lived_labs:
                    is_long_living = True
                    break

            if not is_long_living:
                lab_id = details["id"]
                title = details["lab_title"]
                created_date = datetime.strptime(
                    details["created"], self.created_date_format
                )
                labs[lab_id] = {"title": title, "created_date": created_date}

        return labs

    def stop_labs(self, labs_to_stop: list, email: str) -> bool:
        """Stops the labs, sends the user each lab's yaml file, and messages the user"""

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
                lab.update_lab_groups(
                    [{"id": self.stopped_labs_group, "permission": "read_only"}]
                )
                self.dynamodb.update_cml_lab_stopped(email, lab_id)

                lab_title = lab.title
                message = (
                    "Lab: **"
                    + lab_title
                    + f"**\n - Status: **Stopped** \n - Reason: {reason_lab_stopped}"
                )
                self.webex_api.messages.create(toPersonEmail=email, markdown=message)
            except Exception:
                self.send_admin_error_message()
                self.logging.error("Error wiping lab")

        return True

    def start_delete_process(self, labs_to_delete: dict) -> bool:
        """Starts all the labs and enables the EventBridge Cron Job"""
        self.connect()

        self.logging.info("Start deleting labs")

        # get number nodes started
        base_number_nodes_started = self.get_number_nodes_active()
        if not self.check_able_delete_labs(base_number_nodes_started, labs_to_delete):
            return False

        number_program_started_nodes = 0

        self.logging.info("Base Started Nodes: %d", base_number_nodes_started)

        # Start all labs
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

                # check to see if lab is running
                self.logging.info("Check if lab is started")
                if lab.state() == "STARTED":
                    self.logging.info("Lab %s in started state - resetting in dynamo", lab_title)
                    #self.dynamodb.update_cml_lab_used_date(user_email, lab_id, lab_title)
                    continue

                if max_node_limit_reached:
                    stopped_labs.append(lab_data)
                    continue

                nodes = {"started": {"all": [], "no_license": []}, "stopped": []}
                # try and start as many nodes as possible
                for node in lab.nodes():
                    try:
                        # don't count towards max node count
                        if node.node_definition in self.nodes_not_count_license:
                            node.start(wait=False)
                            nodes["started"]["no_license"].append(node.id)
                            nodes["started"]["all"].append(node.id)

                        elif (
                            base_number_nodes_started + number_program_started_nodes + 1
                            <= self.cml_max_node_count
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
                        if e.response.text == self.node_license_error:
                            max_node_limit_reached = True
                            nodes["stopped"].append(node.id)

                lab_data["nodes"] = nodes
                started_labs.append(lab_data)
            except Exception:
                self.send_admin_error_message()
                self.logging.error("Error deleting lab %s: %s", lab_title, str(e))

        self.logging.info("STARTED LABS: %s", str(started_labs))
        self.logging.info("STOPPED LABS: %s", str(stopped_labs))

        # if len(started_labs) != 0:
        #     self.start_delete_labs_cron_job(
        #         started_labs, stopped_labs, number_program_started_nodes
        #     )

        return True

    def check_lab_converged(self, event: dict) -> bool:
        """Checks if labs have started and deletes them"""
        start_time = time.perf_counter()

        self.logging.info("Check Labs Converge")
        self.logging.warning("CRON JOB STOP TIME = %s", datetime.now().strftime("%H:%M:%S"))

        self.disable_delete_labs_cron_job()
        self.fill_user_labs_dict()

        started_labs = event["started_labs"]
        stopped_labs = event["stopped_labs"]
        number_program_started_nodes = event["number_program_started_nodes"]

        base_number_nodes_started = (
            self.get_number_nodes_active() - number_program_started_nodes
        )

        self.check_able_delete_labs(
            base_number_nodes_started, started_labs + stopped_labs
        )

        max_node_limit_reached = (
            base_number_nodes_started + number_program_started_nodes
            >= self.cml_max_node_count
        )
        self.logging.info("TOTAL BASE NODES STARTED: %d", base_number_nodes_started)

        for lab_data in started_labs.copy():
            try:
                lab_id = lab_data["lab_id"]
                user_email = lab_data["user_email"]
                nodes = lab_data["nodes"]

                lab = self.cml_client.join_existing_lab(lab_id)
                lab_title = lab.title

                self.logging.info("Checking if converged %s", lab_title)

                for node_id in nodes["started"]["all"].copy():
                    node = lab.get_node_by_id(node_id)
                    if node.has_converged():
                        # fetch config from device - exception because certain nodes don't allow extraction
                        self.logging.info("Update configs for node")
                        try:
                            # Make sure won't go out of AWS TIMEOUT
                            if time.perf_counter() - start_time > self.MAX_AWS_TIME:
                                self.start_delete_labs_cron_job(started_labs, stopped_labs)
                            node.extract_configuration()
                        except Exception as e:
                            self.logging.error(
                                "ERROR extracting node config: %s", str(e)
                            )
                        node.stop(wait=True)
                        nodes["started"]["all"].remove(node_id)

                        if node_id in nodes["started"]["no_license"]:
                            nodes["started"]["no_license"].remove(node_id)
                            continue

                        number_program_started_nodes -= 1
                        max_node_limit_reached = False

                if max_node_limit_reached:
                    continue

                for node_id in nodes["stopped"].copy():
                    try:
                        if (
                            base_number_nodes_started + number_program_started_nodes + 1
                            <= self.cml_max_node_count
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
                        self.send_admin_error_message()
                        if e.response.text == self.node_license_error:
                            max_node_limit_reached = True
                            break

                # no more stopped nodes and no started nodes
                if not nodes["stopped"] and not nodes["started"]["all"]:
                    # only download if all nodes gone
                    yaml_string = lab.download()

                    lab.stop()
                    lab.wipe()
                    lab.remove()
                    self.send_lab_topology(yaml_string, lab_title, user_email)
                    self.dynamodb.delete_cml_lab(user_email, lab.id)
                    started_labs.remove(lab_data)

            except Exception as e:
                self.send_admin_error_message()
                self.logging.error("Error deleting lab %s: %s", lab_title, str(e))

        # start more labs
        if not max_node_limit_reached:
            # try and start a non-started lab
            for lab_data in stopped_labs.copy():
                lab_id = lab_data["lab_id"]
                user_email = lab_data["user_email"]

                lab = self.cml_client.join_existing_lab(lab_id)
                lab_title = lab.title

                # try and start as many nodes as possible
                nodes = {"started": {"all": [], "no_license": []}, "stopped": []}
                for node in lab.nodes():
                    try:
                        if node.node_definition in self.nodes_not_count_license:
                            node.start(wait=False)
                            nodes["started"]["no_license"].append(node.id)
                            nodes["started"]["all"].append(node.id)

                        elif (
                            base_number_nodes_started + number_program_started_nodes + 1
                            <= self.cml_max_node_count
                        ):
                            node.start(wait=False)
                            nodes["started"]["all"].append(node.id)
                            number_program_started_nodes += 1

                        else:
                            max_node_limit_reached = True
                            nodes["stopped"].append(node.id)
                    except HTTPError as e:
                        self.send_admin_error_message()
                        if e.response.text == self.node_license_error:
                            max_node_limit_reached = True
                            nodes["stopped"].append(node.id)

                lab_data["nodes"] = nodes
                started_labs.append(lab_data)
                stopped_labs.remove(lab_data)

                if max_node_limit_reached:
                    break

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

        # create schedule
        t = datetime.now() + timedelta(minutes=3)
        schedule_string = f"{t.year}-{str(t.month).zfill(2)}-{str(t.day).zfill(2)}T{str(t.hour).zfill(2)}:{str(t.minute).zfill(2)}:{str(t.second).zfill(2)}"

        self.eventbridge_scheduler.update_schedule(
            FlexibleTimeWindow={
                'Mode': 'OFF'
            },
            Name='CML-Lab-Delete-Schedule',
            ScheduleExpression=f'at({schedule_string})',
            ScheduleExpressionTimezone='UTC',
            State='ENABLED',
            Target={
                'Arn': self.delete_labs_cron_job_arn,
                'RoleArn': 'arn:aws:iam::326674879808:role/colabot-lambda-execution'
            }
        )

        event = {
            "type": "continue_cron_job",
            "number_program_started_nodes": number_program_started_nodes,
            "started_labs": started_labs,
            "stopped_labs": stopped_labs,
        }

        self.eventbridge_client.put_targets(
            Rule=self.delete_labs_cron_job_name,
            Targets=[
                {
                    "Id": self.delete_labs_cron_job_id,
                    "Arn": self.delete_labs_cron_job_arn,
                    "Input": json.dumps(event),
                }
            ],
        )

        self.eventbridge_client.enable_rule(Name=self.delete_labs_cron_job_name)

        self.logging.warning("CRON JOB START TIME = %s", datetime.now().strftime("%H:%M:%S"))

        return True

    def disable_delete_labs_cron_job(self) -> bool:
        """Disables cron job and"""
        self.eventbridge_client.put_targets(
            Rule=self.delete_labs_cron_job_name,
            Targets=[
                {
                    "Id": self.delete_labs_cron_job_id,
                    "Arn": self.delete_labs_cron_job_arn,
                    "Input": "",
                }
            ],
        )

        self.eventbridge_client.disable_rule(Name=self.delete_labs_cron_job_name)

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
                        and node.node_definition not in self.nodes_not_count_license
                    ):
                        number_of_active_nodes += 1

        return number_of_active_nodes

    def check_able_delete_labs(self, base_number_nodes_running, all_labs) -> bool:
        """If too many base nodes are started, exits function and notifies admins"""

        if base_number_nodes_running < self.cml_max_node_count:
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
            roomId=self.admin_webex_room_id, markdown=message
        )

        sys.exit(1)


    def send_admin_error_message(self):
        # Stop all labs if critical

        message = f"An error was encoutered while running CML managing: <pre>{traceback.format_exc()}</code></pre>"

        self.webex_api.messages.create(
            roomId=self.admin_webex_room_id, markdown=message
        )
