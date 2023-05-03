import logging
import datetime
import json
import os
import sys
from awslambda.iam.KeyManager import KeyManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, handle):
    logger.info('new event received: %s', str(event))
    logger.info(str(event))
    logger.info(str(handle))
    start_time = datetime.datetime.now()

    if "DAYS_TO_ROTATE" in os.environ and "DAYS_TO_WARN" in os.environ and "DAYS_TO_DELETE" in os.environ and "IAM_GROUP" in os.environ:
        rotate_days = os.getenv("DAYS_TO_ROTATE")
        rotate_delete_days = os.getenv("ROTATE_DAYS_TO_DELETE")
        group = os.getenv("IAM_GROUP")
        unused_warn_days = os.getenv("UNUSED_WARN_DAYS")
        unused_delete_days = os.getenv("UNUSED_DELETE_DAYS")
    else:
        logging.error("Environment variable(s) DAYS_TO_ROTATE, DAYS_TO_WARN and DAYS_TO_DELETE must be set")
        sys.exit(1)

    key_manager = KeyManager(group=group, rotate_days=rotate_days, unused_delete_days=unused_delete_days, unused_warn_days=unused_warn_days, rotate_delete_days=rotate_delete_days)
    success_count, fail_count = key_manager.rotate_keys()

    logger.info("Succesful user iterations: %d", success_count)
    logger.info("Failed user iterations: %d", fail_count)

    end_time = datetime.datetime.now()
    logger.info('Script complete, total runtime {%s - %s}', end_time, start_time)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({"testkey ": "testval"})
    }
