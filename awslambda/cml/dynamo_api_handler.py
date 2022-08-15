import logging
import os
import sys
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr


class Dynamoapi:
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
        self.logging = logging.getLogger()

        if "DYNAMODB_CML_LABS_TABLE" in os.environ:
            self.db_cml_name = os.getenv("DYNAMODB_CML_LABS_TABLE")
        else:
            logging.error("Environment variable DYNAMODB_CML_LABS_TABLE must be set")
            sys.exit(1)

        self.cml_table = None
        self.dynamodb = None
        self.table_date_format = "%m%d%Y"
        self.cml_labs_tag = '#cml_labs'

    def get_dynamo_cml_table(self):
        """
        if not already done, creates a dynamodb session and switches the current table to the room table

        return: None
        """
        if self.dynamodb is None:
            self.dynamodb = boto3.resource("dynamodb")
        if self.cml_table is None:
            self.cml_table = self.dynamodb.Table(self.db_cml_name)

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

        table_labs = response["Items"][0]["cml_labs"]
        labs = {}
        for lab_id, lab_created_date in table_labs.items():
            labs[lab_id] = (
                datetime.strptime(lab_created_date, self.table_date_format)
            ).date()

        return labs

    def add_cml_lab(self, email: str, lab_id: str, date: datetime.date):
        """Adds a new lab to a user - has to have cml_labs field"""
        self.get_dynamo_cml_table()
        date_string = datetime.strftime(date, self.table_date_format)

        response = self.cml_table.query(
            KeyConditionExpression=Key("email").eq(email),
            FilterExpression=Attr("cml_labs").exists(),
        )

        # create cml_labs field if it doesn't exist
        if response["Count"] == 0:
            self.cml_table.update_item(
                Key={"email": email},
                UpdateExpression="SET #cml_labs= :value",
                ExpressionAttributeNames={self.cml_labs_tag: "cml_labs"},
                ExpressionAttributeValues={":value": {}},
            )

        try:
            self.cml_table.update_item(
                Key={"email": email},
                UpdateExpression="set #cml_labs.#lab_id= :lab",
                ExpressionAttributeNames={
                    self.cml_labs_tag: "cml_labs",
                    "#lab_id": lab_id,
                },
                ExpressionAttributeValues={":lab": date_string},
            )
        except Exception as e:
            self.logging.debug("Error: %s", e)

    def delete_cml_lab(self, email: str, lab_id: str):
        """Adds a new lab to a user - has to have cml_labs field"""
        self.get_dynamo_cml_table()

        try:
            self.cml_table.update_item(
                Key={"email": email},
                UpdateExpression="remove #cml_labs.#lab_id",
                ExpressionAttributeNames={
                    self.cml_labs_tag: "cml_labs",
                    "#lab_id": lab_id,
                },
            )
        except Exception as e:
            self.logging.debug("Error: %s", e)
