import logging
import datetime
import json
import os
import sys
from awslambda.KeyManager import KeyManager

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, handle):
    logger.debug('new event received: %s', str(event))
    logger.debug(str(event))
    logger.debug(str(handle))
    start_time = datetime.datetime.now()

    if "DAYS_TO_ROTATE" in os.environ and "DAYS_TO_WARN" in os.environ and "DAYS_TO_DELETE" in os.environ and "IAM_GROUP" in os.environ:
        rotate_days = os.getenv("DAYS_TO_ROTATE")
        warn_days = os.getenv("DAYS_TO_WARN")
        delete_days = os.getenv("DAYS_TO_DELETE")
        group = os.getenv("IAM_GROUP")
    else:
        logging.error("Environment variable(s) DAYS_TO_ROTATE, DAYS_TO_WARN and DAYS_TO_DELETE must be set")
        sys.exit(1)

    key_manager = KeyManager(group=group, rotate_days=rotate_days, warn_days=warn_days, delete_days=delete_days)
    key_manager.rotate_keys()

    end_time = datetime.datetime.now()
    logger.debug('Script complete, total runtime {%s - %s}', end_time, start_time)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({"testkey ": "testval"})
    }
