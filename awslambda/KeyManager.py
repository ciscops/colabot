import logging
import os


class KeyManager:
    def __init__(self, group, rotate_days, warn_days, delete_days):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
        self.logging = logging.getLogger()

        self.delete_days = delete_days
        self.group = group
        self.rotate_days = rotate_days
        self.user = ""
        self.warn_days = warn_days

    def rotate_keys(self):
        self.logging.debug("")
        # get iam user iterator
        # for user in iterator
            # set self.user to user to be used later
            # get iam user key iterator
            # for key in key iterator
                # process key
                # self.process_key(key, user):

        return ""

    def process_key(self):
        self.logging.debug("")
        # get key age

        # if (key age >= 80):
            # if (key age == 80):
                # self.create_new_key():
                # self.warn_user():
                # return

            # if (key age >= 90):
                # self.delete_key():
                # return

            # self.warn_user(): key >= 80, isn't 80, isnt >= 90 (80 < key < 90)
            # warns user key is expiring in 90 - age days
            # return

        # get key last used
        # if (key LU > 40):
            # if (key LU > 45):
            # self.delete_key():
            # return

        # self.warn_user()
