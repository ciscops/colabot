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
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
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
        # for user in users:
        #   grab all labs
        #   updates labs in database
        #   for each lab
        #       perform various checks
        #   Do all actions

        success_counter = 0
        fail_counter = 0

        self.logging.info("Managing Labs")

        self.cml_api.fill_user_labs_dict()
        all_user_emails = self.dynamodb.get_all_cml_users()

        for user_email in all_user_emails:

            if self.cml_api.user_in_long_lived_labs(user_email):
                continue

            # grab all labs from both cml and database
            user_cml_labs = self.cml_api.get_user_labs(user_email)
            user_database_labs = self.dynamodb.get_cml_user_labs(user_email)

            # delete any labs in database that are not in cml server
            self.update_user_database_labs(
                user_database_labs, user_cml_labs, user_email
            )

            labs_to_wipe = []
            labs_to_delete = []
            labs_warning_wiped = []
            labs_warning_deleted = []

            for lab_id, (
                lab_title,
                lab_last_used_date,
                lab_is_wiped,
                lab_wiped_date,
                card_sent_date,
                user_responded_date,
            ) in user_database_labs.items():

                # check see if user was sent a card and never responded in time
                if self.lab_to_wipe(card_sent_date, user_responded_date):
                    self.logging.info("Adding lab to be wiped")
                    labs_to_wipe.append(lab_id)

                # check see if within deletion period
                elif self.lab_to_delete(lab_is_wiped, lab_last_used_date):
                    self.logging.info("Adding lab to be deleted")
                    labs_to_delete.append(lab_id)

                # check see if lab within warning wiped period
                elif self.lab_to_warn_wiping(lab_last_used_date, user_responded_date):
                    self.logging.info("Adding lab to warning for being wiped")
                    labs_warning_wiped.append((lab_id, lab_title, lab_last_used_date))

                # check see if lab within wiped period
                elif self.lab_to_warn_delete(lab_is_wiped, lab_wiped_date):
                    self.logging.info("Adding lab to warning for being wiped")
                    labs_warning_deleted.append((lab_title, lab_last_used_date))

            # Delete labs
            self.cml_api.delete_labs(labs_to_delete, user_email)

            # Wipe labs
            self.cml_api.wipe_labs(labs_to_wipe, user_email)

            # Send card warning labs to be wiped
            if labs_warning_wiped:
                self.send_labbing_card(labs_warning_wiped, user_email)

            # Send card warning labs to be deleted
            if labs_warning_deleted:
                self.send_deletion_card(labs_warning_wiped, user_email)

        return (success_counter, fail_counter)

    def update_user_database_labs(
        self, user_database_labs: dict, user_cml_labs: dict, user_email: str
    ) -> bool:
        """Adds labs from cml to database and Deletes an labs in database that are not in the labs' source of truth"""
        for cml_lab_id in user_cml_labs:
            if cml_lab_id not in user_database_labs:
                self.logging.info("ADD %s adding lab to database", user_email)
                lab_last_used_date = user_cml_labs[cml_lab_id]["created_date"]
                self.dynamodb.add_cml_lab(user_email, cml_lab_id, lab_last_used_date)
                user_database_labs[cml_lab_id] = lab_last_used_date

        for lab_id in user_database_labs:
            if lab_id not in user_cml_labs:
                self.logging.info("DELETE %s Deleting lab from database", user_email)
                self.dynamodb.delete_cml_lab(user_email, lab_id)
                del user_database_labs[lab_id]

        return True

    def lab_to_warn_wiping(
        self,
        lab_last_used_date: date,
        user_responded_date: date,
    ) -> bool:
        """Determines if lab within wiping warning period"""
        if (date.today() - lab_last_used_date).days >= self.WARN_DAYS:
            return True

        # If card sent AND user responded, see if already past warn days
        if user_responded_date + self.WARN_DAYS >= date.today():
            # THIS IS REDUNDANT IF lab_last_used_date is updated to responded_date when user responds
            return True

        return False

    def lab_to_warn_delete(self, lab_is_wiped: bool, lab_wiped_date: date) -> bool:
        """Checks if lab within deletion warning period"""

        if lab_is_wiped and lab_wiped_date + self.DELETE_WARNING_DAYS >= date.today():
            return True

        return False

    def lab_to_wipe(self, card_sent_date: date, user_responded_date: date) -> bool:
        """Checks see if a person did not respond to card in time and auto wipes the lab"""
        if user_responded_date == 0:
            # User never responded
            return False

        if card_sent_date > user_responded_date + self.WIPE_DAYS:
            return True

        return False

    def lab_to_delete(self, lab_is_wiped: bool, lab_last_used_date: date) -> bool:
        """Checks if lab has been wiped and over the wiped-to-delete period"""
        if not lab_is_wiped:
            return False

        if lab_last_used_date + self.DELETE_DAYS >= date.today():
            return True

        return False

    def send_deletion_card(self, labs_to_send: list, user_email: str) -> bool:
        """Sends the deletion card to the user with the labs to be deleted"""
        message = "The following labs are scheduled to be deleted. If you would like to keep your lab, please start it."
        for lab_title, last_used_date in labs_to_send:
            last_seen = (date.today() - last_used_date).days
            message += f"\n- Lab: {lab_title} | Last seen: {last_seen} days ago"

        card_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "deletion_card.json"
        )

        render_variables = {"message": message}

        self.logging.info("Sending warning deletion card")
        self.send_card(card_file, render_variables, user_email)

        return True

    def send_labbing_card(self, labs_to_send: list, user_email: str) -> bool:
        """Sends the labbing card to the user with labs to be wiped"""

        card_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "labbing_card.json"
        )

        lab_choices = []
        all_lab_ids = ""
        for lab_id, lab_title, last_used_date in labs_to_send:
            last_seen = (date.today() - last_used_date).days
            lab = {
                "title": f"Lab: {lab_title} | Last seen: {last_seen} days ago",
                "value": lab_id,
            }
            lab_choices.append(lab)

            all_lab_ids += f"{lab_id},"

        all_lab_ids = all_lab_ids[:-1]

        render_variables = {
            "lab_choices": json.dumps(lab_choices),
            "all_lab_ids": json.dumps(all_lab_ids),
            "user_email": json.dumps(user_email),
        }
        self.logging.info("Sending labbing card")
        self.send_card(card_file, render_variables, user_email)

        return True

    def send_card(
        self, card_file: str, render_variables: dict, user_email: str
    ) -> bool:
        """Sends the card_file to the user with the rendered_variables"""

        self.logging.info("CARD: %s", str(card_file))
        with open(f"{card_file}", encoding="utf8") as file_:
            template = Template(file_.read())
        card = template.render(render_variables)
        card_json = json.loads(card)

        self.logging.info("CARD %s", str(card_json))

        self.webex_api.messages.create(
            toPersonEmail=user_email, markdown="Labbing", attachments=card_json
        )

        return True
