import logging
import os
import datetime


class KeyManager:
    def __init__(self, group, rotate_days, warn_days, delete_days):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
        self.logging = logging.getLogger()

        if "AWS_ACCESS_KEY_ID_COLABOT" in os.environ and "AWS_SECRET_ACCESS_KEY_COLABOT" in os.environ:
            self.access_key_id = os.getenv("AWS_ACCESS_KEY_ID_COLABOT")
            self.access_key_secret = os.getenv("AWS_SECRET_ACCESS_KEY_COLABOT")
        else:
            logging.error("Environment variable(s) AWS_ACCESS_KEY_ID_COLABOT and AWS_SECRET_ACCESS_KEY_COLABOT must be set")
            sys.exit(1)

        if "WEBEX_BOT_ID_COLABOT" in os.environ and "WEBEX_BOT_ACCESS_KEY_COLABOT" in os.environ:
            self.webex_bot_id = os.getenv("WEBEX_BOT_ID_COLABOT")
            self.webex_bot_access_key = os.getenv("WEBEX_BOT_ACCESS_KEY_COLABOT")
        else:
            logging.error("Environment variable(s) AWS_ACCESS_KEY_ID_COLABOT and AWS_SECRET_ACCESS_KEY_COLABOT must be set")
            sys.exit(1)

        self.client = boto3.client("iam", aws_access_key_id=self.r53_id, aws_secret_access_key=self.r53_key)
        self.delete_days = delete_days
        self.group = group
        self.rotate_days = rotate_days
        self.user = ""
        self.warn_days = warn_days

    def rotate_keys(self, iam_group_name):
        self.logging.debug("")
        rotation_result_flag = True
        iam_group = self.client.Group(iam_group_name)
        iam_group_users = iam_group.users.all()

        for user in iam_group_users:
            self.logging.debug("Checking keys for user: %s", user.name())
            user_access_key_list = user.access_keys.all()

            # function  call to dynamodb for username

            for access_key in user_access_key_list:
                rotation_result_flag = self.process_key(access_key, user)

        return rotation_result_flag

    def process_key(self, access_key, user):
        key_age = datetime.datetime.today() - access_key.create_date
        key_status = access_key.status
        key_id = access_key.create_date

        if key_status == "Active":
            if (key_age >= 80):
                if (key_age == 80):
                    self.logging.debug("")
                    # self.create_new_key():
                    # self.warn_user():
                    # return
                if (key_age >= 90):
                    # self.delete_key():
                    # return

                # self.warn_user(): key >= 80, isn't 80, isnt >= 90 (80 < key < 90)
                # warns user key is expiring in 90 - age days
                # return

            key_last_used = self.client.get_access_key_last_used(AccessKeyId=key_id)
            if (key_last_used >= 40):
                if (key_last_used > 45):
                    # self.delete_key():
                    # return
                # self.warn_user()

        return True
        # condition: return true if everything worked successfully
        # if there was an error, return false
