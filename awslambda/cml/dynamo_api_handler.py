import logging
import os
import sys
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr


class Dynamoapi:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
        self.logging = logging.getLogger()

        try:
            self.DB_CML_NAME = os.environ["DYNAMODB_CML_LABS_TABLE"]
        except KeyError as e:
            logging.error("Environment variable %s must be set", str(e))
            sys.exit(1)

        self.cml_table = None
        self.dynamodb = None
        self.CML_LABS_TAG = "#cml_labs"
        self.LAB_ID_TAG = "#lab_id"

    def get_dynamo_cml_table(self):
        """
        if not already done, creates a dynamodb session and switches the current table to the room table

        return: None
        """
        if self.dynamodb is None:
            self.dynamodb = boto3.resource("dynamodb")
        if self.cml_table is None:
            self.cml_table = self.dynamodb.Table(self.DB_CML_NAME)

    def get_all_cml_users(self) -> list:
        """gets all the user emails from the cml database"""
        self.get_dynamo_cml_table()
        all_emails = self.cml_table.scan()

        emails = []
        for user in all_emails["Items"]:
            emails.append(user["email"])
        self.logging.debug("EMAILS: %s", str(emails))
        return emails

    def get_cml_user_labs(self, user_email: str) -> dict:
        """
        gets all cml users and their labs

        return: dictionary pair of lab (id) and last_used date (data) {lab_id: last_used}
        """
        self.logging.info("Email %s", user_email)
        self.get_dynamo_cml_table()
        response = self.cml_table.query(
            KeyConditionExpression=Key("email").eq(user_email),
            FilterExpression=Attr("cml_labs").exists(),
        )

        if response["Count"] == 0:
            return {}

        response = self.cml_table.query(
            KeyConditionExpression=Key("email").eq(user_email)
        )

        # Turn into dictionary
        table_labs = response["Items"][0]["cml_labs"]
        for lab_id in table_labs:
            for key, val in table_labs[lab_id].items():
                try:
                    if isinstance(table_labs[lab_id][key], bool):
                        continue
                    time_ = datetime.fromtimestamp(int(val))
                    table_labs[lab_id][key] = time_
                except Exception:
                    pass

        return table_labs

    def add_cml_lab(
        self, email: str, lab_id: str, lab_title: str, created_date: datetime
    ):
        """Adds a new lab to a user"""
        self.get_dynamo_cml_table()
        date_string = str(int(datetime.timestamp(created_date)))

        response = self.cml_table.query(
            KeyConditionExpression=Key("email").eq(email),
            FilterExpression=Attr("cml_labs").exists(),
        )

        # create cml_labs field if it doesn't exist
        if response["Count"] == 0:
            self.cml_table.update_item(
                Key={"email": email},
                UpdateExpression="SET #cml_labs= :value",
                ExpressionAttributeNames={self.CML_LABS_TAG: "cml_labs"},
                ExpressionAttributeValues={":value": {}},
            )

        # insert new lab
        self.cml_table.update_item(
            Key={"email": email},
            UpdateExpression="SET #cml_labs.#lab_id= :lab_data",
            ExpressionAttributeNames={
                self.CML_LABS_TAG: "cml_labs",
                self.LAB_ID_TAG: lab_id,
            },
            ExpressionAttributeValues={
                ":lab_data": {
                    "lab_title": lab_title,
                    "lab_is_stopped": False,
                    "lab_stopped_date": "",
                    "card_sent_date": "",
                    "user_responded_date": date_string,
                    "lab_discovered_date": date_string,
                }
            },
        )

    def update_cml_lab_used_date(
        self,
        email: str,
        lab_id: str,
        lab_title: str,
        update_date: datetime = datetime.now(),
    ):
        """Updates the last used date for a lab"""
        self.add_cml_lab(email, lab_id, lab_title, update_date)

    def update_cml_lab_stopped(
        self, email: str, lab_id: str, lab_stopped_date: datetime = datetime.now()
    ):
        """Updates the stopped lab fields"""
        self.get_dynamo_cml_table()
        date_string = str(int(datetime.timestamp(lab_stopped_date)))

        self.cml_table.update_item(
            Key={"email": email},
            UpdateExpression=(
                """SET #cml_labs.#lab_id.#lab_stopped_date= :value1, #cml_labs.#lab_id.#lab_stopped= :value2,"""
                """#cml_labs.#lab_id.#card_sent_date= :value3"""
            ),
            ExpressionAttributeNames={
                self.CML_LABS_TAG: "cml_labs",
                self.LAB_ID_TAG: lab_id,
                "#lab_stopped_date": "lab_stopped_date",
                "#lab_stopped": "lab_is_stopped",
                "#card_sent_date": "card_sent_date",
            },
            ExpressionAttributeValues={
                ":value1": date_string,
                ":value2": True,
                ":value3": "",
            },
        )

    def update_cml_lab_card_sent(
        self, email: str, lab_id: str, card_sent_date: datetime = datetime.now()
    ):
        """Updates the card_sent_date field"""
        self.get_dynamo_cml_table()
        date_string = str(int(datetime.timestamp(card_sent_date)))

        self.cml_table.update_item(
            Key={"email": email},
            UpdateExpression="SET #cml_labs.#lab_id.#card_sent_date= :date",
            ExpressionAttributeNames={
                self.CML_LABS_TAG: "cml_labs",
                self.LAB_ID_TAG: lab_id,
                "#card_sent_date": "card_sent_date",
            },
            ExpressionAttributeValues={":date": date_string},
        )

    def delete_cml_lab(self, email: str, lab_id: str):
        """Deletes a lab from a user - Note: user has to have cml_labs field"""
        self.get_dynamo_cml_table()

        try:
            self.cml_table.update_item(
                Key={"email": email},
                UpdateExpression="remove #cml_labs.#lab_id",
                ExpressionAttributeNames={
                    self.CML_LABS_TAG: "cml_labs",
                    self.LAB_ID_TAG: lab_id,
                },
            )
        except Exception as e:
            self.logging.error("Problem deleting lab: %s", str(e))
