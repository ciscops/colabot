import logging
import os
import sys
from datetime import date
from webexteamssdk import WebexTeamsAPI
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

        if "WEBEX_TEAMS_ACCESS_TOKEN" in os.environ:
            self.webex_bot_access_key = os.getenv("WEBEX_TEAMS_ACCESS_TOKEN")
        else:
            logging.error("Environment variable WEBEX_TEAMS_ACCESS_TOKEN must be set")
            sys.exit(1)

        if "DYNAMODB_TABLE_NAME" in os.environ:
            self.dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME")
        else:
            logging.error("Environment variable(s) DYNAMODB_TABLE_NAME must be set")
            sys.exit(1)

        ###MADE UP KEY DATES FOR TESTING
        if "CREATED_DAYS" in os.environ:
            self.created_days = os.getenv("CREATED_DAYS")
        else:
            logging.error("Environment variable(s) CREATED_DAYS must be set")
            sys.exit(1)
        if "KEY_LAST_USED" in os.environ:
            self.key_last_used = os.getenv("KEY_LAST_USED")
        else:
            logging.error("Environment variable(s) KEY_LAST_USED must be set")
            sys.exit(1)
        if "KEY_STATUS" in os.environ:
            self.key_status = os.getenv("KEY_STATUS")
        else:
            logging.error("Environment variable(s) KEY_STATUS must be set")
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

        self.api = WebexTeamsAPI()
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.dynamodb_table_name)
        self.delete_days = int(delete_days)
        self.group = group
        self.rotate_days = int(rotate_days)
        self.warn_days = int(warn_days)

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
                for access_key in user_access_key_list:
                    self.process_key(access_key, user_email, user)

    def process_key(self, access_key, user_email, user):
        # key_age = access_key.create_date
        # currentdate = date.today()
        # key_created_days = (currentdate - key_age.date()).days
        key_created_days = self.created_days

        # key_status = access_key.status
        key_status = self.key_status
        key_id = access_key.access_key_id
        # access_key_last_used = self.client.get_access_key_last_used(AccessKeyId=key_id)
        access_key_last_used = self.key_last_used

        self.logging.debug("Email: %s", user_email)
        self.logging.debug("Key status: %s ", key_status)
        self.logging.debug("key is %s days old", key_created_days)

        if key_status != "Active":
            self.delete_key(
                user_email=user_email,
                key_id=key_id,
                expired=True,
                unused=False,
                key_created_days=key_created_days,
                user=user,
            )
            return

        if key_created_days >= self.rotate_days:
            if key_created_days == self.rotate_days:
                # Key age is 80, create a new key and deliver to user. Also warn user their now old key will expire in 90 - key age
                self.create_new_key(
                    user_email=user_email,
                    key_id=key_id,
                    user=user,
                )

                return
            if key_created_days >= self.delete_days:
                # key age is >= 90 days old delete key tells the user it's deleted
                self.delete_key(
                    user_email=user_email,
                    key_id=key_id,
                    expired=True,
                    unused=False,
                    key_created_days=key_created_days,
                    user=user,
                )
                return
            # Key age is between 81 and 89 days, warn user that their key is expiring in 90 - key age
            self.warn_user(
                user_email=user_email,
                expire=True,
                unused=False,
                days_to_warn=key_created_days,
                key_id=key_id,
            )
            return

        if "LastUsedDate" in access_key_last_used["AccessKeyLastUsed"]:
            key_last_used = access_key_last_used["AccessKeyLastUsed"]["LastUsedDate"]
            key_last_used_date = (currentdate - key_last_used.date()).days
            self.logging.debug("Key was last used %s days ago", key_last_used_date)
            if (
                key_last_used_date >= self.warn_days - 5
            ):  # If key is within 5 days of unused deadline
                if key_last_used_date >= self.warn_days:
                    # key last used > 45
                    self.delete_key(
                        user_email=user_email,
                        key_id=key_id,
                        expired=False,
                        unused=True,
                        key_created_days=key_created_days,
                        user=user,
                    )
                    return

                # Key was last used between 40 and 45 days
                self.warn_user(
                    user_email=user_email,
                    expire=False,
                    unused=True,
                    days_to_warn=key_last_used_date,
                    key_id=key_id,
                )
                return

        self.logging.debug("Key is within acceptable usage timeframes")

    def create_new_key(self, user_email, key_id, user):
        # access_key_pair = user.create_access_key_pair()
        # new_access_key_id = access_key_pair.access_key_id
        # new_secret_access_key = access_key_pair.secret_access_key
        new_access_key_id = "123456789"
        new_secret_access_key = "MYSECRETTOKEN"

        message = (
            f"Current access key is {self.rotate_days} days old, a new access key has been created. "
            + f"\n - Old access key {key_id} has {self.delete_days - self.rotate_days} days left before it is expired."
            + f"\n - New access key **Access key ID** = ({new_access_key_id}) | **Secret access key** = ({new_secret_access_key})"
        )

        # This script only runs if two key exist, which presumes 1 key is within expiring and 1 is not given the bot can do what it needs to
        # double check that a static message like this is fine
        self.logging.debug("Current key is %s days old, creating new access key", str(self.rotate_days))
        self.send_message_to_user(user_email, message)

    def delete_key(self, user_email, key_id, expired, unused, key_created_days, user):
        # access_key = user.AccessKey(key_id)
        # access_key.delete()

        message = ""
        if expired:
            message = f"Access key ({key_id}) \n - Age: {key_created_days} days old \n - Maximum lifespan: {self.delete_days} days \n - Status: **Deleted** \n - Reason: exceeds lifespan"
            self.logging.debug("Key is %s old or older, deleting key", str(self.delete_days))
        if unused:
            message = f"Access key ({key_id}) \n - Last used: {self.warn_days} days ago \n - Maximum unused lifespan: {self.warn_days} days \n - Status: **Deleted** \n - Reason: key is not used"
            self.logging.debug("Key has not been used in %s days, deleting key", str(self.warn_days))

        self.send_message_to_user(user_email, message)

    def warn_user(self, user_email, expire, unused, days_to_warn, key_id):
        message = ""
        if expire:
            message = f"Access key ({key_id}) \n - Age: {days_to_warn} days old \n - Expiration in: {self.delete_days - days_to_warn} days \n - Status: **Warning** \n - Reason: reaching key age limit of {self.delete_days} days \n"
            self.logging.debug(
                "Key age is between %s-%s days old, warning user of expiration", str(self.rotate_days), str(self.delete_days)
            )
        if unused:
            message = f"Access key ({key_id}) \n - Last used: {days_to_warn} days ago \n - Expiration in: {self.warn_days - days_to_warn} days \n - Status: **Warning** \n - Reason: reaching key unused limit of {self.warn_days} days \n"
            self.logging.debug(
                "Key has not been used in %s-%s days, warning user of expiration", str(self.warn_days-5), str(self.warn_days)
            )

        self.send_message_to_user(user_email, message)

    def send_message_to_user(self, user_email, message):
        self.logging.debug("Sending message to %s", user_email)
        self.api.messages.create(toPersonEmail=user_email, markdown=message)

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
