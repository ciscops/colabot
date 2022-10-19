import logging
import os
import sys
import tempfile
from datetime import datetime
import yaml
from virl2_client import ClientLibrary
from webexteamssdk import WebexTeamsAPI
from awslambda.cml.dynamo_api_handler import Dynamoapi


class CMLAPI:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
        self.logging = logging.getLogger()

        if "CML_USERNAME" in os.environ:
            self.cml_username = os.getenv("CML_USERNAME")
        else:
            logging.error("Environment variable CML_USERNAME must be set")
            sys.exit(1)

        if "CML_PASSWORD" in os.environ:
            self.cml_password = os.getenv("CML_PASSWORD")
        else:
            logging.error("Environment variable CML_PASSWORD must be set")
            sys.exit(1)

        if "LONG_LIVED_LABS_GROUP" in os.environ:
            self.long_lived_labs = os.getenv("LONG_LIVED_LABS_GROUP")
        else:
            logging.error("Environment variable LONG_LIVED_LABS_GROUP must be set")
            sys.exit(1)

        if "WIPED_LABS_GROUP" in os.environ:
            self.wiped_labs_group = os.getenv("WIPED_LABS_GROUP")
        else:
            logging.error("Environment variable WIPED_LABS_GROUP must be set")
            sys.exit(1)

        if "LAB_DELETE_DAYS" in os.environ:
            self.DELETE_DAYS = int(os.getenv("LAB_DELETE_DAYS"))
        else:
            logging.error("Environment variable LAB_DELETE_DAYS must be set")
            sys.exit(1)

        self.client = None
        self.webex_api = WebexTeamsAPI()
        self.dynamodb = Dynamoapi()
        self.created_date_format = "%Y-%m-%dT%H:%M:%S+00:00"
        self.user_and_labs = {}
        self.long_lived_users = []

    def connect(self):
        """starts connection to cml api if there is none"""
        if self.client is None:
            url = "https://cpn-rtp-cml-stable1.ciscops.net/"
            self.client = ClientLibrary(
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
        diagnostics = self.client.get_diagnostics()

        self.logging.debug("iterating through users")
        for user in diagnostics["user_list"]:
            if user["username"] != "ppajersk":
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
            lab = self.client.join_existing_lab(lab_id)
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

    def wipe_labs(self, labs_to_wipe: list, email: str) -> bool:
        """Wipes the labs, sends the user each lab's yaml file, and messages the user"""

        if not labs_to_wipe:
            return False

        self.connect()
        for lab_dict in labs_to_wipe:
            try:
                lab_id = lab_dict["lab_id"]
                reason_lab_wiped = lab_dict["reason_lab_wiped"]

                lab = self.client.join_existing_lab(lab_id)

                lab.stop()
                lab.wipe()
                self.logging.info("Stopped and wiped lab")
                lab.update_lab_groups(
                    [{"id": self.wiped_labs_group, "permission": "read_only"}]
                )
                self.dynamodb.update_cml_lab_wiped(email, lab_id)

                lab_title = lab.title
                message = (
                    "Lab: **"
                    + lab_title
                    + f"**\n - Status: **Wiped** \n - Reason: {reason_lab_wiped}"
                )
                self.webex_api.messages.create(toPersonEmail=email, markdown=message)
            except Exception:
                self.logging.error("Error wiping lab")

        return True

    def delete_labs(self, lab_ids: list, user_email: str) -> bool:
        """Deletes the given labs from cml and the database"""
        self.connect()

        for lab_id in lab_ids:
            try:
                lab = self.client.join_existing_lab(lab_id)
                lab_title = lab.title

                # check to see if lab is running

                if lab.state() == "STARTED":
                    self.dynamodb.update_cml_lab_used_date(
                        user_email, lab_id, lab_title
                    )
                    continue

                yaml_string = lab.download()

                lab.remove()
                self.send_lab_topology(yaml_string, lab_title, user_email)
                self.dynamodb.delete_cml_lab(user_email, lab_id)

            except Exception:
                self.logging.error("Error deleting lab %s", lab_title)

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
                + f"**\n - Status: **Deleted** \n - Reason: Exceeded {self.DELETE_DAYS} wiped timeframe",
                files=[outfile.name],
            )

        return True

    def check_lab_active(self, lab_id: str) -> bool:
        """Returns whether a lab is active or not"""
        lab = self.client.join_existing_lab(lab_id)
        return lab.state() == "STARTED"
