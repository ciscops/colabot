import logging
import sys
import os
from datetime import date
from webexteamssdk import WebexTeamsAPI
from awslambda.cml.dynamo_api_handler import Dynamoapi
from awslambda.cml.cml_api_handler import CMLAPI


class CMLManager:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
        self.logging = logging.getLogger()

        if "LAB_WARN_DAYS" in os.environ:
            self.WARN_DAYS = int(os.getenv("LAB_WARN_DAYS"))
        else:
            logging.error("Environment variable LAB_WARN_DAYS must be set")
            sys.exit(1)

        if "WEBEX_TEAMS_ACCESS_TOKEN" in os.environ:
            self.wxt_access_token = os.getenv("WEBEX_TEAMS_ACCESS_TOKEN")
        else:
            logging.error("Environment variable WEBEX_TEAMS_ACCESS_TOKEN must be set")
            sys.exit(1)

        self.dynamodb = Dynamoapi()
        self.cml_api = CMLAPI()
        self.webex_api = WebexTeamsAPI()

    def manage_labs(self):
        """
        Main function for managing cml labs within an acceptable time frame
        1. populates/deletes labs from database
        2. warns users about labs to be wiped
        """
        success_counter = 0
        fail_counter = 0

        self.logging.debug("Managing Labs")
        self.cml_api.connect()
        all_user_emails = self.dynamodb.get_all_cml_users()
        self.cml_api.fill_user_labs_dict()

        for email in all_user_emails:
            try:
                cml_labs = self.cml_api.get_user_labs(email)
                database_labs = self.dynamodb.get_cml_user_labs(email)

                # delete any labs not in cml server
                for lab_id in database_labs:
                    if lab_id not in cml_labs:
                        self.logging.debug("DELETE %s Deleting lab from database", email)
                        self.dynamodb.delete_cml_lab(email, lab_id)

                # compares cml labs to last_used date in database
                labs_to_wipe = []
                for cml_lab_id, (cml_lab_title, cml_lab_date) in cml_labs.items():
                    if cml_lab_id not in database_labs:
                        self.logging.debug("ADD %s adding lab to database", email)
                        self.dynamodb.add_cml_lab(email, cml_lab_id, cml_lab_date)
                        database_labs[cml_lab_id] = cml_lab_date

                    last_used_date = database_labs[cml_lab_id]
                    if (date.today() - last_used_date).days >= self.WARN_DAYS:
                        self.logging.debug("ADD %s adding lab to be wiped", email)
                        labs_to_wipe.append((cml_lab_id, cml_lab_title, last_used_date))

                self.logging.info("%s LABS_TO_WIPE: %s", email, labs_to_wipe)
                success_counter += 1
            except Exception as e:
                self.logging.error("ERROR: %s", str(e))
                fail_counter += 1

        return (success_counter, fail_counter)
