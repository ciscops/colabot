import logging
import os
import sys
import tempfile
from datetime import datetime
import json
import yaml
import boto3
from virl2_client import ClientLibrary
from webexteamssdk import WebexTeamsAPI
from awslambda.cml.dynamo_api_handler import Dynamoapi


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

        self.cml_username = os.getenv("CML_USERNAME")
        self.cml_password = os.getenv("CML_PASSWORD")
        self.long_lived_labs = os.getenv("LONG_LIVED_LABS_GROUP")
        self.stopped_labs_group = os.getenv("STOPPED_LABS_GROUP")
        self.DELETE_DAYS = int(os.getenv("LAB_DELETE_DAYS"))
        self.delete_labs_cron_job_name = os.getenv("DELETE_LABS_CRON_JOB_NAME")
        self.delete_labs_cron_job_id = os.getenv("DELETE_LABS_CRON_JOB_ID")
        self.delete_labs_cron_job_arn = os.getenv("DELETE_LABS_CRON_JOB_ARN")

        self.eventbridge_client = boto3.client("events")
        self.cml_client = None
        self.webex_api = WebexTeamsAPI()
        self.dynamodb = Dynamoapi()
        self.created_date_format = "%Y-%m-%dT%H:%M:%S+00:00"
        self.user_and_labs = {}
        self.long_lived_users = []

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
            if user["username"] not in ("kstickne", "ppajersk"):
                continue
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
        """Wipes the labs, sends the user each lab's yaml file, and messages the user"""

        if not labs_to_stop:
            return False

        self.connect()
        for lab_dict in labs_to_stop:
            try:
                lab_id = lab_dict["lab_id"]
                reason_lab_stopped = lab_dict["reason_lab_stopped"]

                lab = self.cml_client.join_existing_lab(lab_id)

                lab.stop()
                self.logging.info("Stopped lab")
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
                self.logging.error("Error wiping lab")

        return True

    def start_delete_process(self, labs_to_delete: dict) -> bool:
        """Starts all the labs and enables the EventBridge Cron Job"""
        self.connect()

        self.logging.info("Start deleting labs")

        # Start all labs
        started_labs = []
        self.logging.info("Starting labs")
        for lab_data in labs_to_delete:
            lab_id = lab_data["lab_id"]
            user_email = lab_data["user_email"]

            lab = self.cml_client.join_existing_lab(lab_id)
            lab_title = lab.title

            # check to see if lab is running
            self.logging.info("Check if lab is started")
            if lab.state() == "STARTED":
                self.dynamodb.update_cml_lab_used_date(user_email, lab_id, lab_title)
                continue

            lab.start(wait=False)
            started_labs.append(lab_data)

        if len(started_labs) != 0:
            self.start_delete_labs_cron_job(started_labs)

        return True

    def check_lab_converged(self, event: dict) -> bool:
        """Checks if labs have started and deletes them"""

        self.disable_delete_labs_cron_job()
        self.connect()
        started_labs = event["started_labs"]

        for lab_data in started_labs.copy():
            try:
                lab_id = lab_data["lab_id"]
                user_email = lab_data["user_email"]

                lab = self.cml_client.join_existing_lab(lab_id)

                self.logging.info("Checking if converged")
                if not lab.has_converged():
                    continue

                # fetch config from device - exception because certain nodes don't allow extraction
                self.logging.info("Update configs")
                for node in lab.nodes():
                    try:
                        node.extract_configuration()
                    except Exception as e:
                        self.logging.error("ERROR extracting node config: %s", str(e))
                lab.stop(wait=False)

                lab_title = lab.title
                yaml_string = lab.download()

                # lab.wipe()
                # lab.remove()
                self.send_lab_topology(yaml_string, lab_title, user_email)
                # self.dynamodb.delete_cml_lab(user_email, lab.id)

                started_labs.remove(lab_data)

            except Exception:
                self.logging.error("Error deleting lab %s", lab_title)

        if len(started_labs) != 0:
            self.start_delete_labs_cron_job(started_labs)

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

    def start_delete_labs_cron_job(self, started_labs: list) -> bool:
        """Enables the delete labs cron job"""

        event = {"type": "continue_cron_job", "started_labs": started_labs}

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

    def get_number_nodes_active(self) -> int:
        """Returns the number of active nodes"""
        number_of_active_nodes = 0
        for user_labs in self.user_and_labs.values():
            for lab_id in user_labs:
                lab = self.cml_client.join_existing_lab(lab_id)
                for node in lab.nodes():
                    if node.is_active():
                        number_of_active_nodes += 1

        return number_of_active_nodes
        # nodes_to_turn_on = len(labs.nodes())

