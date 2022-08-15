import logging
import os
import sys
from datetime import datetime
from virl2_client import ClientLibrary


class CMLAPI:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
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

        self.client = None
        self.created_date_format = "%Y-%m-%dT%H:%M:%S+00:00"
        self.user_and_labs = {}

    def connect(self):
        """starts connection to cml api if there is none"""
        if self.client is None:
            url = "https://cpn-rtp-cml-stable1.ciscops.net/"
            self.client = ClientLibrary(
                url, self.cml_username, self.cml_password, ssl_verify=False
            )

    def fill_user_labs_dict(self) -> dict:
        """gets all user emails and labs from cml"""
        self.connect()
        diagnostics = self.client.get_diagnostics()
        for user in diagnostics["user_list"]:
            self.user_and_labs[user["username"] + "@cisco.com"] = user["labs"]

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
