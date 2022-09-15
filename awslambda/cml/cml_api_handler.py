import logging
import os
import sys
import tempfile
from datetime import datetime
import yaml
from virl2_client import ClientLibrary, models
from webexteamssdk import WebexTeamsAPI


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

        self.client = None
        self.webex_api = WebexTeamsAPI()
        self.created_date_format = "%Y-%m-%dT%H:%M:%S+00:00"
        self.user_and_labs = {}
        self.long_lived_users = []

    def connect(self):
        """starts connection to cml api if there is none"""
        if self.client is None:
            url = "https://cpn-rtp-cml-stable1.ciscops.net/"
            self.client = ClientLibrary(
                url, self.cml_username, self.cml_password, ssl_verify=False
            )

    def fill_user_labs_dict(self) -> dict:
        """gets all user emails and labs from cml as well as seeing if user in long lived labs group"""
        self.connect()
        diagnostics = self.client.get_diagnostics()
        for user in diagnostics["user_list"]:
            email = user["username"] + "@cisco.com"
            self.user_and_labs[email] = user["labs"]

            for group in user["groups"]:
                if group["id"] == self.long_lived_labs:
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
                created_date_full = datetime.strptime(
                    details["created"], self.created_date_format
                )
                created_date = created_date_full.date()
                labs[lab_id] = (title, created_date)

        return labs

    def wipe_labs(self, lab_ids: list, email: str) -> bool:
        """Wipes the labs, sends the user each lab's yaml file, and messages the user"""

        self.connect()
        for lab_id in lab_ids:
            try:
                lab = self.client.join_existing_lab(lab_id)
                lab_name = lab.title

                lab.stop()
                lab.wipe()
                self.logging.info("Stopped and wiped lab")
                self.send_lab_topology(lab, email)
                lab.update_lab_groups(
                    [{"id": self.wiped_labs_group, "permission": "read_only"}]
                )
            except Exception:
                self.logging.error("Error wiping lab")

        return True

    def send_lab_topology(self, lab: models.lab.Lab, email) -> bool:
        """Downloads the lab and sends it to the user"""
        lab_name = lab.title
        yaml_string = lab.download()
        self.logging.info("Sending Topology file to user")

        with open(
            tempfile.NamedTemporaryFile(
                suffix=".yaml", prefix=f'{lab_name.replace(" ","_")}_'
            ).name,
            "w",
            encoding="utf-8",
        ) as outfile:
            yaml.dump(yaml.full_load(yaml_string), outfile, default_flow_style=False)

            self.webex_api.messages.create(
                toPersonEmail=email,
                markdown=f'Your lab "{lab_name}" has been wiped. Attached is the YAML Topology file',
                files=[outfile.name],
            )

        return True
