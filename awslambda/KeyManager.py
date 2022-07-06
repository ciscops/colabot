import logging
import os
import sys
from datetime import date
import boto3
from boto3.dynamodb.conditions import Key, Attr


class KeyManager:
    def __init__(self, group, rotate_days, warn_days, delete_days):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
        self.logging = logging.getLogger()

        if (
            "AWS_ACCESS_KEY_ID_COLABOT" in os.environ
            and "AWS_SECRET_ACCESS_KEY_COLABOT" in os.environ
        ):
            self.access_key_id = os.getenv("AWS_ACCESS_KEY_ID_COLABOT")
            self.access_key_secret = os.getenv("AWS_SECRET_ACCESS_KEY_COLABOT")
        else:
            logging.error(
                "Environment variable(s) AWS_ACCESS_KEY_ID_COLABOT and AWS_SECRET_ACCESS_KEY_COLABOT must be set"
            )
            sys.exit(1)

        if (
            "WEBEX_BOT_ID_COLABOT" in os.environ
            and "WEBEX_BOT_ACCESS_KEY_COLABOT" in os.environ
        ):
            self.webex_bot_id = os.getenv("WEBEX_BOT_ID_COLABOT")
            self.webex_bot_access_key = os.getenv("WEBEX_BOT_ACCESS_KEY_COLABOT")
        else:
            logging.error(
                "Environment variable(s) AWS_ACCESS_KEY_ID_COLABOT and AWS_SECRET_ACCESS_KEY_COLABOT must be set"
            )
            sys.exit(1)

        if "DYNAMODB_TABLE_NAME" in os.environ:
            self.dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME")
        else:
            logging.error("Environment variable(s) DYNAMODB_TABLE_NAME must be set")
            sys.exit(1)

        self.resource = boto3.resource(
            "iam",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.access_key_secret,
        )
        self.client = boto3.client(
            "iam",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.access_key_secret,
        )

        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.dynamodb_table_name)
        self.delete_days = delete_days
        self.group = group
        self.rotate_days = rotate_days
        self.user = ""
        self.warn_days = warn_days

    def rotate_keys(self):
        self.logging.debug("")
        iam_group = self.resource.Group(self.group)
        iam_group_users = iam_group.users.all()

        for user in iam_group_users:
            name = user.name
            user_access_key_list = user.access_keys.all()
            user_email = self.get_dynamo_user_email(name)

            if user_email is not None:
                self.logging.debug("Checking keys for user: %s", name)
                response = self.client.list_access_keys(UserName=name)
                if len(response['AccessKeyMetadata']) <= 2:
                    for access_key in user_access_key_list:
                        self.process_key(access_key, user_email)

                if len(response['AccessKeyMetadata']) > 2:
                    self.logging.debug("User has too many keys")
                    # What happens here, do we iterate through all the keys and remove any
                    # till the user has only 2 keys left?

    def process_key(self, access_key, user_email):
        key_age = access_key.create_date
        currentdate = date.today()
        key_created_days = (currentdate - key_age.date()).days

        key_status = access_key.status
        key_id = access_key.access_key_id
        access_key_last_used = self.client.get_access_key_last_used(AccessKeyId=key_id)

        self.logging.debug("Email: %s", user_email)
        self.logging.debug("Key status: %s ", key_status)
        self.logging.debug("key is %s days old", key_created_days)

        if key_status != "Active":
            return

        if key_created_days >= 80:
            if key_created_days == 80:
                # self.logging.debug("Key age is 80")
                # self.create_new_key():
                # self.warn_user():
                return
            if key_created_days >= 90:
                # self.logging.debug("key age is >= 90")
                # self.delete_key():
                return

            # self.logging.debug("Key age is between 81 and 89")
            # self.warn_user(): key >= 80, isn't 80, isnt >= 90 (80 < key < 90)
            # warns user key is expiring in 90 - age days
            return

        if "LastUsedDate" in access_key_last_used["AccessKeyLastUsed"]:
            key_last_used = access_key_last_used["AccessKeyLastUsed"]["LastUsedDate"]
            key_last_used_date = (currentdate - key_last_used.date()).days
            self.logging.debug("Key was last used %s days ago", key_last_used_date)
            if key_last_used_date >= 40:
                if key_last_used_date > 45:
                    # self.logging.debug("key last used > 45")
                    # self.delete_key():
                    return

                # Key was last used between 40 and 45 days
                # self.warn_user()
                return

        self.logging.debug("Key is within acceptable usage timeframes")

    def get_dynamo_user_email(self, user_name):
        response = self.table.query(
            KeyConditionExpression=Key("email").eq(user_name + "@cisco.com")
        )

        if len(response["Items"]) > 0:
            return response["Items"][0]["email"]

        table_scan_data = self.table.scan(
            FilterExpression=Attr("username").contains(user_name)
        )

        if len(table_scan_data["Items"]) > 0:
            return table_scan_data["Items"][0]["email"]

        return None
