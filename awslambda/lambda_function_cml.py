import logging
import datetime
import json
from awslambda.cml.cml_manager import CMLManager
from awslambda.cml.dynamo_api_handler import Dynamoapi

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, handle):
    logger.debug('new event received: %s', str(event))
    logger.debug(str(event))
    logger.debug(str(handle))
    start_time = datetime.datetime.now()

    dynamodb = Dynamoapi()

    all_user_emails = dynamodb.get_all_cml_users()
    cml = CMLManager()
    success_count, fail_count = cml.manage_labs(all_user_emails)

    logger.debug("Succesful user iterations: %d", success_count)
    logger.debug("Failed user iterations: %d", fail_count)

    end_time = datetime.datetime.now()
    logger.debug('Script complete, total runtime {%s - %s}', end_time, start_time)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({"testkey ": "testval"})
    }
