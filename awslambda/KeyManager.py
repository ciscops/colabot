import logging
import os

class KeyManager:
    def __init__(self, group, rotate_days, warn_days, delete_days):
        # Initialize logging
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
        self.logging = logging.getLogger()

        self.group = group
        self.rotate_days = rotate_days
        self.warn_days = warn_days
        self.delete_days = delete_days
        self.user = ""

    def rotate_keys(self):
        self.logging.debug("")
        return ""

    def process_key(self):
        self.logging.debug("")
