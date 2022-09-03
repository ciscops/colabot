import logging
import sys
import os
import json
from datetime import date
from jinja2 import Template
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

        if "LAB_DELETE_DAYS" in os.environ:
            self.DELETE_DAYS = int(os.getenv("LAB_DELETE_DAYS"))
        else:
            logging.error("Environment variable LAB_DELETE_DAYS must be set")
            sys.exit(1)

        if "WEBEX_TEAMS_ACCESS_TOKEN" in os.environ:
            self.wxt_access_token = os.getenv("WEBEX_TEAMS_ACCESS_TOKEN")
        else:
            logging.error("Environment variable WEBEX_TEAMS_ACCESS_TOKEN must be set")
            sys.exit(1)

        self.dynamodb = Dynamoapi()
        self.cml_api = CMLAPI()
        self.webex_api = WebexTeamsAPI()

    def manage_labs(self) -> tuple:
        """Main function for managing cml labs"""
        all_user_emails = self.dynamodb.get_all_cml_users()

        # Update database and send labs to be wiped cards
        success_count, fail_count = self.update_labs_in_database(all_user_emails)
        self.logging.info("Succesful user iterations update send cards: %d", success_count)
        self.logging.info("Failed user iterations send cards: %d", fail_count)

        # Delete labs greater than given wiped period
        success_count, fail_count = self.delete_wiped_labs(all_user_emails)
        self.logging.info("Succesful user iterations delete labs: %d", success_count)
        self.logging.info("Failed user iterations delete labs: %d", fail_count)

        # Warn for labs to be deleted

        return (0,0)

    def delete_wiped_labs(self, user_emails: list) -> tuple:
        """Delete labs that have been wiped and over the wiped-to-delete period"""
        success_counter = 0
        fail_counter = 0

        for user_email in user_emails:
            try:
                labs_to_delete = []
                wiped_labs = self.dynamodb.get_wiped_labs(user_email)
                for lab_id, lab_last_used in wiped_labs:
                    if lab_last_used + self.DELETE_DAYS >= date.today():
                        labs_to_delete.append(lab_id)

                self.cml_api.delete_labs(labs_to_delete, user_email)
                success_counter += 1
            except Exception as e:
                self.logging.error("Error deleting lab %s: %s", lab_id, str(e))
                fail_counter += 1

        return (success_counter, fail_counter)

    def update_labs_in_database(self, user_emails: list) -> tuple:
        """
        Updates all the labs from CML into the database
        1. populates/deletes labs from database
        2. warns users about labs to be wiped
        """
        success_counter = 0
        fail_counter = 0

        self.logging.debug("Managing Labs")
        self.cml_api.fill_user_labs_dict()

        for email in user_emails:
            try:
                self.logging.info("Checking labs for user %s", email)

                self.cml_api.check_card_timeframe(email) #check if already sent card and if user responded

                if self.cml_api.user_in_long_lived_labs(email):
                    continue

                cml_labs = self.cml_api.get_user_labs(email)
                database_labs = self.dynamodb.get_cml_user_labs(email)

                # delete any labs not in cml server
                self.delete_extra_database_labs(database_labs, cml_labs, email)

                # compares cml labs to last_used date in database
                labs_to_send_card = self.get_labs_to_send_card(
                    database_labs, cml_labs, email
                )

                # check any cards already sent to user
                labs_to_send_card = self.check_sent_cards_dates(
                    database_labs, cml_labs, labs_to_send_card, email
                )

                self.logging.info("%s labs_to_send_card: %s", email, labs_to_send_card)

                # Send card
                if labs_to_send_card:
                    self.logging.info("Sending labbing card to %s", email)
                    self.send_labbing_card(labs_to_send_card, email)

                success_counter += 1
            except Exception as e:
                self.logging.error("ERROR: %s", str(e))
                fail_counter += 1

        return (success_counter, fail_counter)

    def get_labs_to_send_card(
        self, database_labs: dict, cml_labs: dict, email: str
    ) -> list:
        """Creates a list of labs that need to be wiped and adds labs to the database"""
        labs_to_send_card = []
        for cml_lab_id, (cml_lab_title, cml_lab_date) in cml_labs.items():
            if cml_lab_id not in database_labs:
                self.logging.debug("ADD %s adding lab to database", email)
                self.dynamodb.add_cml_lab(email, cml_lab_id, cml_lab_date)
                database_labs[cml_lab_id] = cml_lab_date

            last_used_date = database_labs[cml_lab_id]
            if (date.today() - last_used_date).days >= self.WARN_DAYS:
                self.logging.debug("ADD %s adding lab to be wiped", email)
                labs_to_send_card.append((cml_lab_id, cml_lab_title, last_used_date))

        return labs_to_send_card

    def delete_extra_database_labs(
        self, database_labs: dict, cml_labs: dict, email: str
    ) -> bool:
        """Deletes an labs in database that are not in the labs' source of truth"""
        for lab_id in database_labs:
            if lab_id not in cml_labs:
                self.logging.debug("DELETE %s Deleting lab from database", email)
                self.dynamodb.delete_cml_lab(email, lab_id)

        return True

    def send_labbing_card(self, labs_to_send_card: list, email: str) -> bool:
        """Sends the labbing card to the user with labs to be wiped"""
        lab_choices = []
        all_lab_ids = ""
        for lab_id, lab_title, last_used_date in labs_to_send_card:
            last_seen = (date.today() - last_used_date).days
            lab = {
                "title": f"Lab: {lab_title} | Last seen: {last_seen} days ago",
                "value": lab_id,
            }
            lab_choices.append(lab)

            all_lab_ids += f"{lab_id},"

        all_lab_ids = all_lab_ids[:-1]
        self.logging.debug("LAB: %s", str(lab_choices))

        card_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "labbing_card.json"
        )
        self.logging.debug("CARD: %s", str(card_file))
        with open(f"{card_file}", encoding="utf8") as file_:
            template = Template(file_.read())
        card = template.render(
            lab_choices=json.dumps(lab_choices),
            all_lab_ids=json.dumps(all_lab_ids),
            email=json.dumps(email),
        )
        card_json = json.loads(card)

        self.logging.debug("CARD %s", str(card_json))

        self.webex_api.messages.create(
            toPersonEmail=email, markdown="labbing", attachments=card_json
        )

        return True

    def check_sent_cards_dates(
        self, database_labs: dict, cml_labs: dict, labs_to_send_card: list, email: str
    ) -> list:
        """Checks see if a person did not respond to card in time and auto wipes the lab"""

        labs_to_wipe = []
        for cml_lab_id, cml_data in cml_labs.items():
            cml_lab_title = cml_data[0]
            responded_date = database_labs[cml_lab_id]["card_responded_date"]
            card_sent_date = database_labs[cml_lab_id]["card_sent_date"]

            if card_sent_date > responded_date + self.WIPE_DAYS:
                # user not responded to card in time -> wipe labs
                labs_to_wipe.append(cml_lab_id)

            elif responded_date + self.WARN_DAYS >= date.today():
                # last response more than the warning period -> add to labbing card
                last_used_date = database_labs[cml_lab_id]
                labs_to_send_card.append((cml_lab_id, cml_lab_title, last_used_date))

        self.cml_api.wipe_labs(labs_to_wipe, email)

        return labs_to_send_card
