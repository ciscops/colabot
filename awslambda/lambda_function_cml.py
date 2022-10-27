import logging
import datetime
import json
from awslambda.cml.cml_manager import CMLManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, handle):
    logger.debug('new event received: %s', str(event))
    logger.debug(str(event))
    logger.debug(str(handle))
    start_time = datetime.datetime.now()

    cml = CMLManager()
    success_count, fail_count = cml.manage_labs()

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
