import logging
import sys
import os
import json
from jinja2 import Template
from webexteamssdk import WebexTeamsAPI
from awslambda.cml.dynamo_api_handler import Dynamoapi
from awslambda.cml.cml_api_handler import CMLAPI
from datetime import timedelta


class CMLManager:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
        self.logging = logging.getLogger()

        if "LAB_WARN_DAYS" in os.environ:
            self.WARN_DAYS = os.getenv("LAB_WARN_DAYS")
        else:
            logging.error("Environment variable LAB_WARN_DAYS must be set")
            sys.exit(1)
        
        if 'WEBEX_TEAMS_ACCESS_TOKEN' in os.environ:
            self.wxt_access_token = os.getenv("WEBEX_TEAMS_ACCESS_TOKEN")
        else:
            logging.error("Environment variable WEBEX_TEAMS_ACCESS_TOKEN must be set")
            sys.exit(1)

        if "WEBEX_BOT_ID" in os.environ:
            self.webex_bot_id = os.getenv("WEBEX_BOT_ID")
        else:
            logging.error("Environment variable WEBEX_BOT_ID must be set")
            sys.exit(1)

        self.dynamodb = Dynamoapi()
        self.cml_api = CMLAPI()
        self.webex_api = WebexTeamsAPI()

    def manage_keys(self):
        print("Managing Keys")
        self.cml_api.connect()
        all_user_emails = self.dynamodb.get_all_cml_users()

        for email in all_user_emails:
            cml_labs = self.cml_api.get_user_labs()
            database_labs = self.dynamodb.get_cml_user_labs(email)

            if not cml_labs: #WHAT DO IF has database_labs but no cml_labs??
                continue

            labs_to_wipe = []
            for cml_lab_id, (cml_lab_title, cml_lab_date) in cml_labs.items():
                if cml_lab_id not in database_labs:
                    self.dynamodb.add_cml_lab(email, cml_lab_id, cml_lab_date)
                    continue #don't need to check last_used

                last_used_date = database_labs[cml_lab_id]
                if last_used_date >= cml_lab_date + timedelta(days=self.WARN_DAYS):
                    labs_to_wipe.append((cml_lab_id, cml_lab_title))

            #Send card
            lab_choices = []
            for lab_id,lab_title in labs_to_wipe:
                lab = {
                    "title": f"Lab: {lab_title}",
                    "value": lab_id
                }
                lab_choices.append(lab)

            card_file = "./labbing_card.json"
            with open(f"{card_file}", encoding="utf8") as file_:
                template = Template(file_.read())
            card = template.render(lab_choices=lab_choices)
            card_json = json.loads(card)

            self.webex_api.messages.create(room, markdown="labbing", attachements=card_json)

                



