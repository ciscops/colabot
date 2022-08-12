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

        self.client = None
        self.created_date_format = '%Y-%m-%dT%H:%M:%S+00:00'

    def connect(self):
        if self.client == None:
            url = 'https://cpn-rtp-cml-stable1.ciscops.net/'
            self.client = ClientLibrary(url, self.cml_username, self.cml_password, ssl_verify=False)

    def get_user_labs(self) -> dict:
        """
        Returns a dictionary of the user's labs
        
        return: {id: (title, date_created)}
        s"""
        #TODO: How know which user?? one admin login, or login for each person
        self.connect()
        labs = {}
        for lab in self.client.all_labs():
            details = lab.details()
            id = details['id']
            title = details['lab_title']
            created_date_full = datetime.strptime(details['created'], self.created_date_format)
            created_date = created_date_full.date()
            labs[id] = (title, created_date)

        return labs
