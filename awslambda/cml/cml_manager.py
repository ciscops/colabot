import logging
import sys
import os
import json
from datetime import datetime, timedelta
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

        if "LAB_DELETE_WARNING_DAYS" in os.environ:
            self.DELETE_WARNING_DAYS = int(os.getenv("LAB_DELETE_WARNING_DAYS"))
        else:
            logging.error("Environment variable LAB_DELETE_WARNING_DAYS must be set")
            sys.exit(1)

        if "LAB_CARD_RESPOND_DAYS" in os.environ:
            self.CARD_RESPOND_DAYS = int(os.getenv("LAB_CARD_RESPOND_DAYS"))
        else:
            logging.error("Environment variable LAB_CARD_RESPOND_DAYS must be set")
            sys.exit(1)

        if "LAB_UNWIPED_LIFESPAN" in os.environ:
            self.LAB_UNWIPED_LIFESPAN = int(os.getenv("LAB_UNWIPED_LIFESPAN"))
        else:
            logging.error("Environment variable LAB_UNWIPED_LIFESPAN must be set")
            sys.exit(1)

        if "WEBEX_TEAMS_ACCESS_TOKEN" in os.environ:
            self.wxt_access_token = os.getenv("WEBEX_TEAMS_ACCESS_TOKEN")
        else:
            logging.error("Environment variable WEBEX_TEAMS_ACCESS_TOKEN must be set")
            sys.exit(1)

        self.dynamodb = Dynamoapi()
        self.cml_api = CMLAPI()
        self.webex_api = WebexTeamsAPI()
        self.reason_lab_wiped = ""

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
        # all_user_emails = self.dynamodb.get_all_cml_users()
        all_user_emails = ["kstickne@cisco.com"]

        self.logging.info("Starting users")

        self.logging.info("Starting users")

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

            # grab database labs again since might have been updated
            user_database_labs = self.dynamodb.get_cml_user_labs(user_email)

            labs_to_wipe = []
            labs_to_delete = []
            labs_warning_wiped = []
            labs_warning_deleted = []

            for lab_id, lab_data in user_database_labs.items():
                lab_title = lab_data["lab_title"]
                lab_is_wiped = lab_data["lab_is_wiped"]
                lab_wiped_date = lab_data["lab_wiped_date"]
                card_sent_date = lab_data["card_sent_date"]
                user_responded_date = lab_data["user_responded_date"]
                lab_discovered_date = lab_data["lab_discovered_date"]

                # check see if user was sent a card and never responded in time
                if self.lab_to_wipe(
                    card_sent_date,
                    user_responded_date,
                    lab_discovered_date,
                    lab_is_wiped,
                ):
                    self.logging.info("Adding lab to be wiped")
                    labs_to_wipe.append(
                        {"lab_id": lab_id, "reason_lab_wiped": self.reason_lab_wiped}
                    )

                # check see if lab within warning wiped period
                elif self.lab_to_warn_wiping(
                    user_responded_date, card_sent_date, lab_is_wiped
                ):
                    self.logging.info("Adding lab to warning for being wiped")
                    labs_warning_wiped.append((lab_id, lab_title, user_responded_date))

                # check see if within deletion period
                elif self.lab_to_delete(
                    lab_wiped_date, user_responded_date, lab_is_wiped
                ):
                    self.logging.info("Adding lab to be deleted")
                    labs_to_delete.append(lab_id)

                # check see if lab within wiped period
                elif self.lab_to_warn_delete(
                    lab_wiped_date,
                    user_responded_date,
                    lab_is_wiped,
                    lab_id,
                    lab_title,
                    user_email,
                ):
                    self.logging.info("Adding lab to warning for being wiped")
                    labs_warning_deleted.append((lab_title, lab_wiped_date))

                # Checks to see if a wiped lab has been reactivated
                elif lab_is_wiped and self.cml_api.check_lab_active(lab_id):
                    self.dynamodb.update_cml_lab_used_date(
                        user_email, lab_id, lab_title
                    )

            self.logging.info("WARN WIPE: %s", str(labs_warning_wiped))
            self.logging.info("WIPE: %s", str(labs_to_wipe))
            self.logging.info("WARN DELETE: %s", str(labs_warning_deleted))
            self.logging.info("DELETE: %s", str(labs_to_delete))

                # check see if within deletion period
                elif self.lab_to_delete(lab_is_wiped, user_responded_date):
                    self.logging.info("Adding lab to be deleted")
                    labs_to_delete.append(lab_id)

                # check see if lab within wiped period
                elif self.lab_to_warn_delete(lab_is_wiped, lab_wiped_date):
                    self.logging.info("Adding lab to warning for being wiped")
                    labs_warning_deleted.append((lab_title, user_responded_date))

            self.logging.info("WARN WIPE: %s", str(labs_warning_wiped))
            self.logging.info("WIPE: %s", str(labs_to_wipe))
            self.logging.info("WARN DELETE: %s", str(labs_warning_deleted))
            self.logging.info("DELETE: %s", str(labs_to_delete))

            # # Delete labs
            # self.cml_api.delete_labs(labs_to_delete, user_email)

            # # Wipe labs
            # self.cml_api.wipe_labs(labs_to_wipe, user_email)

            # # Send card warning labs to be wiped
            # self.send_labbing_card(labs_warning_wiped, user_email)

            # Send card warning labs to be deleted
            self.send_deletion_card(labs_warning_deleted, user_email)

            if self.cml_api.user_in_long_lived_labs(user_email):
                continue

    def update_user_database_labs(
        self, user_database_labs: dict, user_cml_labs: dict, user_email: str
    ) -> bool:
        """Adds labs from cml to database and Deletes an labs in database that are not in the labs' source of truth"""
        for cml_lab_id in user_cml_labs:
            if cml_lab_id not in user_database_labs:
                self.logging.info("ADD %s adding lab to database", user_email)
                user_responded_date = user_cml_labs[cml_lab_id]["created_date"]
                lab_title = user_cml_labs[cml_lab_id]["title"]
                self.dynamodb.add_cml_lab(
                    user_email, cml_lab_id, lab_title, user_responded_date
                )

        for lab_id in user_database_labs:
            if lab_id not in user_cml_labs:
                self.logging.info("DELETE %s Deleting lab from database", user_email)
                self.dynamodb.delete_cml_lab(user_email, lab_id)

        return True

    def lab_to_warn_wiping(
        self,
        user_responded_date: datetime,
        card_sent_date: datetime,
        lab_is_wiped: bool,
    ) -> bool:
        """Determines if lab within wiping warning period"""

        if (
            lab_is_wiped
            or isinstance(card_sent_date, datetime)
            or not isinstance(user_responded_date, datetime)
        ):
            return False

        if (datetime.today() - user_responded_date).days > self.WARN_DAYS:
            return True

        return False

    def lab_to_warn_delete(
        self,
        lab_wiped_date: datetime,
        user_responded_date: datetime,
        lab_is_wiped: bool,
        lab_id: str,
        lab_title: str,
        user_email: str,
    ) -> bool:
        """Checks if lab within deletion warning period"""

        if (
            not lab_is_wiped
            or not isinstance(lab_wiped_date, datetime)
            or not isinstance(user_responded_date, datetime)
            or (datetime.today() - user_responded_date).days <= self.WARN_DAYS
        ):
            return False

        if (datetime.today() - lab_wiped_date).days > self.DELETE_WARNING_DAYS:
            # only warn if not active
            if self.cml_api.check_lab_active(lab_id):
                self.dynamodb.update_cml_lab_used_date(user_email, lab_id, lab_title)
                return False
            return True

        return False

    def lab_to_wipe(
        self,
        card_sent_date: datetime,
        user_responded_date: datetime,
        lab_discovered_date: datetime,
        lab_is_wiped: bool,
    ) -> bool:
        """Checks see if a person did not respond to card in time and auto wipes the lab"""

        if lab_is_wiped or not isinstance(user_responded_date, datetime):
            return False

        if (datetime.today() - lab_discovered_date).days > self.LAB_UNWIPED_LIFESPAN:
            # Lab hit hard deadline date
            self.reason_lab_wiped = (
                f"Lab exceeded unwiped {self.LAB_UNWIPED_LIFESPAN} day limit"
            )
            return True

        if (
            not isinstance(card_sent_date, datetime)
            or (datetime.today() - user_responded_date).days <= self.WARN_DAYS
        ):
            return False

        if (datetime.today() - card_sent_date).days > self.CARD_RESPOND_DAYS:
            # User didn't respond in timeframe alloted
            self.reason_lab_wiped = f"User did not respond to card prompt within {self.CARD_RESPOND_DAYS} day limit"
            return True

        return False

    def lab_to_delete(
        self,
        lab_wiped_date: datetime,
        user_responded_date: datetime,
        lab_is_wiped: bool,
    ) -> bool:
        """Checks if lab needs to be deleted"""

        if (
            not lab_is_wiped
            or not isinstance(user_responded_date, datetime)
            or (datetime.today() - user_responded_date).days <= self.WARN_DAYS
        ):
            return False

        # Checks if lab is over the wiped-to-delete period
        if (datetime.today() - lab_wiped_date).days > self.DELETE_DAYS:
            return True

        return False

    def send_deletion_card(self, labs_to_send: list, user_email: str) -> bool:
        """Sends the deletion card to the user with the labs to be deleted"""

        if not labs_to_send:
            return False

        message = "The following labs are scheduled to be deleted. If you would like to keep your lab, please start it.\n"
        for lab_title, lab_wiped_date in labs_to_send:
            days_till_deletion = (
                lab_wiped_date + timedelta(days=self.DELETE_DAYS) - datetime.today()
            ).days

            message += (
                f"\n- Lab: {lab_title} | Days till deletion: {days_till_deletion} days"
            )

        card_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "deletion_card.json"
        )

        render_variables = {"message": json.dumps(message)}

        self.logging.info("Sending warning deletion card")
        self.send_card(card_file, render_variables, user_email)

        return True

    def send_labbing_card(self, labs: list, user_email: str) -> bool:
        """Sends the labbing card to the user with labs to be wiped"""

        if not labs:
            return False

        card_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "labbing_card.json.j2"
        )

        labs_to_send = []
        all_lab_ids = {}
        seperate = "true"
        for lab_id, lab_title, last_used_date in labs:
            last_seen = (datetime.today() - last_used_date).days
            labs_to_send.append(
                {
                    "name": lab_title,
                    "id": lab_id,
                    "last_seen": str(last_seen),
                    "seperator": seperate,
                }
            )
            seperate = "false"
            all_lab_ids[lab_id] = lab_title

        render_variables = {
            "labs": labs_to_send,
            "user_email": user_email,
            "all_lab_ids": all_lab_ids,
            "card_sent_date": int(datetime.today().timestamp()),
            "card_response_limit": self.CARD_RESPOND_DAYS,
        }

        self.logging.info("Sending labbing card")
        self.send_card(card_file, render_variables, user_email)

        for lab_data in labs:
            lab_id = lab_data[0]
            self.dynamodb.update_cml_lab_card_sent(user_email, lab_id)

        return True

    def send_card(
        self, card_file: str, render_variables: dict, user_email: str
    ) -> bool:
        """Sends the card_file to the user with the rendered_variables"""

        with open(f"{card_file}", encoding="utf8") as file_:
            template = Template(file_.read())
        card = template.render(render_variables)
        self.logging.info("CARD: %s", str(card))
        card_json = json.loads(card)

        self.logging.info("CARD %s", str(card_json))

        self.webex_api.messages.create(
            toPersonEmail=user_email,
            markdown="CML Labs - Action Required",
            attachments=card_json,
        )

        return True

    def lab_to_warn_wiping(
        self,
        lab_last_used_date: date,
        user_responded_date: date,
    ) -> bool:
        """Determines if lab within wiping warning period"""

        if lab_is_wiped:
            return False

        if (date.today() - user_responded_date).days >= self.WARN_DAYS:
            return True

        return False

    def lab_to_warn_delete(self, lab_is_wiped: bool, lab_wiped_date: date) -> bool:
        """Checks if lab within deletion warning period"""

        if not lab_is_wiped or not isinstance(lab_wiped_date, date):
            return False
     
        if (date.today() - lab_wiped_date).days >= self.DELETE_WARNING_DAYS:
            # what if they start using it again within that time period - should we see if it's running
            # use user_responded_date or lab_wiped_date?
            return True

        return False

    def lab_to_wipe(self, card_sent_date: date, user_responded_date: date, lab_is_wiped: bool) -> bool:
        """Checks see if a person did not respond to card in time and auto wipes the lab"""

        if (lab_is_wiped or not isinstance(card_sent_date,date) or 
            (date.today() - user_responded_date).days <= self.WARN_DAYS):
            return False
            # Test case: Card_sent_date = 7 days ago, user_responded=3 days ago
            # Don't need this if delete card_sent_date when we update user_reponded_date

        if (date.today() - card_sent_date).days >= self.CARD_RESPOND_DAYS:
            return True

        return False

    def lab_to_delete(self, lab_is_wiped: bool, user_responded_date: date) -> bool:
        """Checks if lab needs to be deleted"""

        if not lab_is_wiped:
            return False

        # Checks if lab is over the wiped-to-delete period
        if (date.today() - user_responded_date).days >= self.DELETE_DAYS:
            # Should we use lab_wiped_date
            return True

        return False

    def send_deletion_card(self, labs_to_send: list, user_email: str) -> bool:
        """Sends the deletion card to the user with the labs to be deleted"""

        if not labs_to_send:
            return False

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

        if not labs_to_send:
            return False

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

        with open(f"{card_file}", encoding="utf8") as file_:
            template = Template(file_.read())
        card = template.render(render_variables)
        self.logging.info("CARD: %s", str(card))
        card_json = json.loads(card)

        self.logging.info("CARD %s", str(card_json))

        self.webex_api.messages.create(
            toPersonEmail=user_email, markdown="Are You Labbing", attachments=card_json
        )

        return True
