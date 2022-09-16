#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
import re
import tempfile
from datetime import datetime, date
import aiohttp
import pymongo
import urllib3
import boto3
from boto3.dynamodb.conditions import Key, Attr
import yaml
from virl2_client import ClientLibrary
from jinja2 import Template
from config import DefaultConfig as CONFIG
from webex import WebExClient
from .CML import CML


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging_message = "This is the aiohttp Client session"
bot_wait_message = "This may take a minute or two..."
https_header = "https://"
botId_regex_pattern = r"1MDFmYzc$"
content_type = "application/json"
awx_server_error_message = "Error contacting AWX server. "
find_user_message = "Cannot find user"
PRE_CODE_SNIPPET = "<pre>"
AFTER_CODE_SNIPPET = "</code></pre>"

mongo_url = (
    "mongodb://"
    + CONFIG.MONGO_INITDB_ROOT_USERNAME
    + ":"
    + CONFIG.MONGO_INITDB_ROOT_PASSWORD
    + "@"
    + CONFIG.MONGO_SERVER
    + ":"
    + CONFIG.MONGO_PORT
)


async def create_accounts(activity):
    cml_servers = CONFIG.SERVER_LIST.split(",")
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
    if activity.get("parentId"):
        message = dict(
            text=bot_wait_message,
            roomId=activity["roomId"],
            parentId=activity["parentId"],
            attachments=[],
        )
        await webex.post_message_to_webex(message)
    else:
        message = dict(
            text=bot_wait_message,
            roomId=activity["roomId"],
            attachments=[],
        )
        await webex.post_message_to_webex(message)
    urls_cml_servers = [https_header + s for s in cml_servers]
    if re.search(botId_regex_pattern, CONFIG.BOT_ID):
        id_template = "14"  # prod
    else:
        id_template = "10"  # for dev
    url = f"https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/"
    headers = {"Content-Type": content_type}
    user_and_domain = activity["sender_email"].split("@")
    body = {
        "extra_vars": {
            "cml_server_list": urls_cml_servers,
            "colab_user_email": activity["sender_email"],
            "colab_user_username": user_and_domain[0],
            "vcenter_address": CONFIG.VCENTER_SERVER,
        }
    }
    auth = aiohttp.BasicAuth(
        login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding="utf-8"
    )
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60), auth=auth)
    logging.debug("%s %s", logging_message, session)
    try:
        async with session.request(
            method="POST", url=url, headers=headers, data=json.dumps(body), ssl=False
        ) as res:
            if res.status != 201:
                if activity.get("parentId"):
                    message = dict(
                        text=awx_server_error_message + str(res.status),
                        roomId=activity["roomId"],
                        parentId=activity["parentId"],
                        attachments=[],
                    )
                else:
                    message = dict(
                        text=awx_server_error_message + str(res.status),
                        roomId=activity["roomId"],
                        attachments=[],
                    )
                await webex.post_message_to_webex(message)
                await session.close()
            else:
                await session.close()
    except Exception as e:
        logging.warning(e)
        if activity.get("parentId"):
            message = dict(
                text=awx_server_error_message + str(res.status),
                roomId=activity["roomId"],
                parentId=activity["parentId"],
                attachments=[],
            )
        else:
            message = dict(
                text=awx_server_error_message + str(res.status),
                roomId=activity["roomId"],
                attachments=[],
            )
        await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e1:
            logging.warning(e1)


async def create_aws_account(activity):
    cml_servers = CONFIG.SERVER_LIST.split(",")
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
    message = dict(
        text=bot_wait_message,
        roomId=activity["roomId"],
        parentId=activity["parentId"],
        attachments=[],
    )
    await webex.post_message_to_webex(message)
    urls_cml_servers = [https_header + s for s in cml_servers]
    if re.search(botId_regex_pattern, CONFIG.BOT_ID):
        id_template = "15"  # prod
    else:
        id_template = "11"  # for dev
    url = f"https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/"
    headers = {"Content-Type": content_type}
    user_and_domain = activity["sender_email"].split("@")
    body = {
        "extra_vars": {
            "cml_server_list": urls_cml_servers,
            "colab_user_email": activity["sender_email"],
            "colab_user_username": user_and_domain[0],
            "vcenter_address": CONFIG.VCENTER_SERVER,
        }
    }
    auth = aiohttp.BasicAuth(
        login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding="utf-8"
    )
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60), auth=auth)
    logging.debug("%s %s", logging_message, session)
    try:
        async with session.request(
            method="POST", url=url, headers=headers, data=json.dumps(body), ssl=False
        ) as res:
            if res.status != 201:
                message = dict(
                    text=awx_server_error_message + str(res.status),
                    roomId=activity["roomId"],
                    parentId=activity["parentId"],
                    attachments=[],
                )
                await webex.post_message_to_webex(message)
                await session.close()
            else:
                await session.close()
    except Exception as e2:
        logging.warning(e2)
        message = dict(
            text=awx_server_error_message + str(res.status),
            roomId=activity["roomId"],
            parentId=activity["parentId"],
            attachments=[],
        )
        await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e3:
            logging.warning(e3)


async def create_vpn_account(activity):
    cml_servers = CONFIG.SERVER_LIST.split(",")
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
    message = dict(
        text=bot_wait_message,
        roomId=activity["roomId"],
        parentId=activity["parentId"],
        attachments=[],
    )
    await webex.post_message_to_webex(message)
    urls_cml_servers = [https_header + s for s in cml_servers]
    if re.search(botId_regex_pattern, CONFIG.BOT_ID):
        id_template = "16"  # prod
    else:
        id_template = "12"  # for dev
    url = f"https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/"
    headers = {"Content-Type": content_type}
    user_and_domain = activity["sender_email"].split("@")
    body = {
        "extra_vars": {
            "cml_server_list": urls_cml_servers,
            "colab_user_email": activity["sender_email"],
            "colab_user_username": user_and_domain[0],
            "vcenter_address": CONFIG.VCENTER_SERVER,
        }
    }
    auth = aiohttp.BasicAuth(
        login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding="utf-8"
    )
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60), auth=auth)
    logging.debug("%s %s", logging_message, session)
    try:
        async with session.request(
            method="POST", url=url, headers=headers, data=json.dumps(body), ssl=False
        ) as res:
            if res.status != 201:
                message = dict(
                    text=awx_server_error_message + str(res.status),
                    roomId=activity["roomId"],
                    parentId=activity["parentId"],
                    attachments=[],
                )
                await webex.post_message_to_webex(message)
                await session.close()
            else:
                await session.close()
    except Exception as e:
        logging.warning(e)
        message = dict(
            text=awx_server_error_message + str(res.status),
            roomId=activity["roomId"],
            parentId=activity["parentId"],
            attachments=[],
        )
        await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e4:
            logging.warning(e4)


async def create_aws_key(activity):
    logging.debug("create aws key")
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])

    user_and_domain = activity["sender_email"].split("@")
    iam_username = user_and_domain[0]
    user = await get_iam_user(iam_username)

    access_key_iterator = user.access_keys.all()
    access_key_list = []
    for key in access_key_iterator:
        access_key_list.append(key)

    # If the user has active access keys that colabot has not expired, don't create keys
    if len(access_key_list) > 0:
        key_message = PRE_CODE_SNIPPET
        for key in access_key_list:
            key_created_days = (date.today() - key.create_date.date()).days
            key_message += f"Key id: {key.access_key_id} | Status: {key.status} | Created: {key_created_days} days ago \n"

        message = dict(
            text=(
                "You already have active aws keys: \n"
                + key_message
                + AFTER_CODE_SNIPPET
                + "\nIf you would like to refresh them, use **reset aws keys**"
            ),
            toPersonId=activity["sender"],
        )
        await webex.post_message_to_webex(message)
        return

    if len(access_key_list) == 0:
        await create_key_and_message_user(activity, user, webex)


async def create_key_and_message_user(activity, user, webex):
    access_key_pair = user.create_access_key_pair()
    new_access_key_id = access_key_pair.access_key_id
    new_secret_access_key = access_key_pair.secret_access_key

    message = dict(
        text=(
            "Access key created: \n"
            + PRE_CODE_SNIPPET
            + "Access Key id: "
            + new_access_key_id
            + "\n"
            + "Access Key secret: "
            + new_secret_access_key
            + "\n"
            + AFTER_CODE_SNIPPET
            + "\nRemember **not to share** your access key id or secret"
        ),
        toPersonId=activity["sender"],
    )

    logging.debug("Sending message to %s", activity["sender"])
    await webex.post_message_to_webex(message)


async def send_reset_keys_confirmation_card(activity):
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])

    user_and_domain = activity["sender_email"].split("@")
    iam_username = user_and_domain[0]
    user = await get_iam_user(iam_username)
    access_key_iterator = user.access_keys.all()

    key_text = "The following keys will be deleted: \n"
    keys = ""
    for key in access_key_iterator:
        key_created_days = (date.today() - key.create_date.date()).days
        days_to_live = 90 - int(key_created_days)
        key_text += f"Id: {key.access_key_id} | Days to Expire: {days_to_live}\n"
        keys += key.access_key_id + ","

    if len(list(access_key_iterator)) == 0:
        message = "You do not have any keys to reset. You can create a key with **create aws key**"
        attachments = []
    else:
        card_file = "./cards/aws_iam_reset_keys.json"
        # verify this doesn't cause problems
        with open(f"{card_file}", encoding="utf8") as file_:
            template = Template(file_.read())
        card = template.render(
            key_choices=json.dumps(key_text),
            username=json.dumps(iam_username),
            keys=json.dumps(keys[:-1]),
        )
        card_json = json.loads(card)
        message = "AWS Reset IAM Keys"
        attachments = [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card_json,
            }
        ]

    message = dict(text=message, roomId=activity["roomId"], attachments=attachments)
    await webex.post_message_to_webex(message)


async def handle_reset_aws_keys_card(activity):
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
    if not activity["inputs"]["isSubmit"]:
        await webex.delete_message(activity["messageId"])

    logging.debug("Activity text %s", activity)

    card_key_choices = activity["inputs"]["ChoiceId"]
    iam_username = activity["inputs"]["username"]

    if card_key_choices == "":
        return

    if card_key_choices != "No":
        card_key_choices = card_key_choices.split(",")
        await reset_aws_key(activity, iam_username, card_key_choices)
        return

    await webex.delete_message(activity["messageId"])


async def reset_aws_key(activity, iam_username, key_list):
    logging.debug("reset aws key")
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
    iam = boto3.resource(
        "iam",
        region_name=CONFIG.AWS_REGION_COLAB,
        aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID_COLAB,
        aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY_COLAB,
    )

    user = await get_iam_user(iam_username, iam)

    await delete_aws_key(activity, iam_username, key_list, iam, webex)
    await create_key_and_message_user(activity, user, webex)


async def send_delete_keys_confirmation_card(activity):
    # send card with cml servers as check boxes
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])

    user_and_domain = activity["sender_email"].split("@")
    iam_username = user_and_domain[0]
    user = await get_iam_user(iam_username)

    access_key_iterator = user.access_keys.all()
    access_key_list = []
    for key in access_key_iterator:
        access_key_list.append(key)

    key_choices = []
    for key in access_key_list:
        key_created_days = (date.today() - key.create_date.date()).days
        days_to_live = 90 - int(key_created_days)
        key_delete_message = f"Id: {key.access_key_id} | Days to Expire: {days_to_live}"

        key_choices.append(
            {"title": f"{key_delete_message}", "value": f"{key.access_key_id}"}
        )

    if len(key_choices) == 0:
        message = "You do not have any keys to delete. You can create a key with **create aws key**"
        attachments = []
    else:
        card_file = "./cards/aws_iam_delete_key.json"
        # verify this doesn't cause problems
        with open(f"{card_file}", encoding="utf8") as file_:
            template = Template(file_.read())
        card = template.render(
            key_choices=json.dumps(key_choices), username=json.dumps(iam_username)
        )
        card_json = json.loads(card)
        message = "AWS Delete IAM Keys"
        attachments = [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card_json,
            }
        ]

    message = dict(text=message, roomId=activity["roomId"], attachments=attachments)
    await webex.post_message_to_webex(message)


async def handle_delete_aws_keys_card(activity):
    if not activity["inputs"]["isSubmit"]:
        webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
        await webex.delete_message(activity["messageId"])

    key_id = activity["inputs"]["keyId"]
    iam_username = activity["inputs"]["username"]

    if key_id != "":
        await delete_aws_key(activity, iam_username, [key_id])


async def delete_aws_key(activity, iam_username, key_list, iam=None, webex=None):
    logging.debug("delete aws key")
    logging.debug("ACTIVITY: %s", str(activity))

    if webex is None:
        webex = WebExClient(webex_bot_token=activity["webex_bot_token"])

    if iam is None:
        iam = boto3.resource(
            "iam",
            region_name=CONFIG.AWS_REGION_COLAB,
            aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID_COLAB,
            aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY_COLAB,
        )

    key_message = PRE_CODE_SNIPPET
    for key_id in key_list:
        access_key = iam.AccessKey(iam_username, key_id)

        try:
            key_message += f"Key: {access_key.access_key_id}\n"
            access_key.delete()
        except Exception as e:
            logging.warning(e)
            print("Cannot delete key")
            return

    message = (
        "The following keys have been deleted:\n" + key_message + AFTER_CODE_SNIPPET
    )

    await webex.edit_message(activity["messageId"], message, activity["roomId"])


async def delete_all_aws_keys(activity, user, webex):
    logging.debug("delete all aws key")
    if webex is None:
        webex = WebExClient(webex_bot_token=activity["webex_bot_token"])

    access_key_iterator = user.access_keys.all()

    key_message = PRE_CODE_SNIPPET
    for access_key in access_key_iterator:
        try:
            key_message += f"Key: {access_key.access_key_id}\n"
            access_key.delete()
        except Exception as e:
            logging.warning(e)
            print("Cannot delete key")
            return

    if key_message != PRE_CODE_SNIPPET:
        message = dict(
            text=(
                "The following keys have been deleted:\n"
                + key_message
                + AFTER_CODE_SNIPPET
            ),
            toPersonId=activity["sender"],
        )
    else:
        message = dict(
            text=("There were no keys to delete"),
            toPersonId=activity["sender"],
        )
    await webex.post_message_to_webex(message)


async def aws_key_status(activity):
    logging.debug("show aws key status")
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])

    user_and_domain = activity["sender_email"].split("@")
    iam_username = user_and_domain[0]
    user = await get_iam_user(iam_username)

    access_key_iterator = user.access_keys.all()
    if len(list(access_key_iterator)) != 0:
        key_message = PRE_CODE_SNIPPET
        for key in access_key_iterator:
            key_created_days = (date.today() - key.create_date.date()).days
            days_to_live = 90 - int(key_created_days)
            key_message += f"Key id: {key.access_key_id} | Status: {key.status} | Days to Expire: {days_to_live} \n"

        message = dict(
            text=("All AWS access keys: \n" + key_message + AFTER_CODE_SNIPPET),
            toPersonId=activity["sender"],
        )
    else:
        message = dict(
            text=("No Aws keys exist. You can create a key with **create aws key**"),
            toPersonId=activity["sender"],
        )

    await webex.post_message_to_webex(message)


async def rotate_aws_key(activity):
    logging.debug("rotate aws key")
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])

    # split the webex username from the domain
    user_and_domain = activity["sender_email"].split("@")
    iam_username = user_and_domain[0]
    user = await get_iam_user(iam_username)

    access_keys = []
    access_key_iterator = user.access_keys.all()
    for access_key in access_key_iterator:
        access_keys.append(access_key)

    # If one key exists, create a second key and message the user
    if len(access_keys) == 1:
        await create_key_and_message_user(activity, user, webex)
        return
    # If two keys exist, delete the oldest, and create a new key and message user
    if len(access_keys) == 2:
        if access_keys[0].create_date > access_keys[1].create_date:
            access_key_delete = access_keys[1]
        else:
            access_key_delete = access_keys[0]

        key_created_days = (date.today() - access_key_delete.create_date.date()).days
        days_to_live = 90 - int(key_created_days)
        key_text = (
            "The following key will be deleted:\n"
            f"Id: {access_key_delete.access_key_id} | Days to Expire: {days_to_live}"
        )

        card_file = "./cards/aws_iam_rotate_keys.json"
        # verify this doesn't cause problems
        with open(f"{card_file}", encoding="utf8") as file_:
            template = Template(file_.read())
        card = template.render(
            key_choice=json.dumps(key_text),
            username=json.dumps(iam_username),
            key=json.dumps(access_key_delete.access_key_id),
        )
        card_json = json.loads(card)

        message = "Confirm rotate keys"
        attachments = card_json

        message = dict(text=message, roomId=activity["roomId"], attachments=attachments)
        await webex.post_message_to_webex(message)
        return

    text_to_send = (
        "You have no active aws keys,"
        + " if you would like to create one, use **create aws key**"
    )
    message = dict(
        text=text_to_send,
        toPersonId=activity["sender"],
    )
    await webex.post_message_to_webex(message)


async def handle_rotate_keys_card(activity):
    """handles the confirmation card for rotate keys"""
    await handle_reset_aws_keys_card(activity)

    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])

    iam_username = activity["inputs"]["username"]
    user = await get_iam_user(iam_username)

    await create_key_and_message_user(activity, user, webex)


async def handle_labbing_card(activity):
    """handles the are cml lab check in card"""
    card_type = activity["inputs"]["isLabbing"]
    selected_labs = activity["inputs"]["labIds"]
    all_labs = activity["inputs"]["allLabIds"]
    user_email = activity["inputs"]["email"]
    labs_not_selected = (set(all_labs)).symmetric_difference(set(selected_labs))

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=CONFIG.AWS_REGION,
        aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY,
    )

    table = dynamodb.Table(
        "colab_directory_dev"
    )  # TODO remove dev extension when pushing to prod

    # if cardType is selection, keep all selected labs, and wipe the other labs
    if card_type == "selection":
        if len(selected_labs) == 0:
            logging.debug("No labs selected, wiping all labs")
            await wipe_and_delete_labs(activity, all_labs, user_email, table)
            return

        logging.debug("Labs selected, wiping unselected labs")
        await wipe_and_delete_labs(activity, labs_not_selected, user_email, table)
        await update_used_labs_in_dynamo(selected_labs, user_email, table)
        return

    if card_type == "none":
        logging.debug("None button selected, wiping all labs")
        await wipe_and_delete_labs(activity, all_labs, user_email, table)
        return

    if card_type == "all":
        logging.debug("all selected, keep all")
        await update_used_labs_in_dynamo(selected_labs, user_email, table)


async def wipe_and_delete_labs(activity, labs, user_email, table):
    """Wipes the labs, sends the user each lab's yaml file, and messages the user"""
    cml_server = CONFIG.SERVER_LIST.split(",")[0]
    logging.debug("CML Server is: %s", cml_server)
    user_and_domain = user_email.split("@")
    cml_password = await get_cml_password(user_email, table)
    cml_user = CML(user_and_domain[0], cml_password, cml_server)

    for lab_id in labs:
        cml_user.wipe_lab(lab_id)
        await download_and_send_lab_toplogy(activity, lab_id, cml_server, user_email)
        await delete_lab_from_dynamo(user_email, lab_id, table)
        cml_user.delete_lab(lab_id)


async def get_cml_password(user_email, table):
    """Gets the user's cml password"""
    response = table.query(
        KeyConditionExpression=Key("email").eq(user_email)
    )

    return response["Items"][0]['password']


async def update_used_labs_in_dynamo(labs, user_email, table):
    """Updates the information of the current used labs"""
    for lab in labs:
        try:
            date_responded = datetime.strftime(date.today(), "%m%d%Y")

            table.update_item(
                Key={"email": user_email},
                UpdateExpression="set #cml_labs.#lab_id.#responded= :card_responded_date",
                ExpressionAttributeNames={
                    "#cml_labs": "cml_labs",
                    "#lab_id": lab,
                    "#responded": "card_responded_date",
                },
                ExpressionAttributeValues={":card_responded_date": date_responded},
            )
        except Exception as e:
            logging.error("Problem updating lab used date: %s", str(e))


async def delete_lab_from_dynamo(user_email, lab_id, table):
    """Deletes the lab from the dynamoDB table"""

    try:
        table.update_item(
            Key={"email": user_email},
            UpdateExpression="remove #cml_labs.#lab_id",
            ExpressionAttributeNames={
                "#cml_labs": "cml_labs",
                "#lab_id": lab_id,
            },
        )
    except Exception as e:
        logging.error("Problem deleting lab: %s", str(e))


async def download_and_send_lab_toplogy(activity, lab_id, cml_server, user_email):
    """Downloads the lab-to-be-wiped topology and sends it to the user"""
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
    url = "https://" + cml_server + "/"
    client = ClientLibrary(
        url,
        CONFIG.CML_USERNAME,
        CONFIG.CML_PASSWORD,
        ssl_verify=False,
        raise_for_auth_failure=True,
    )

    lab = client.join_existing_lab(lab_id)
    lab_title = lab.title
    yaml_string = lab.download()

    with open(
        tempfile.NamedTemporaryFile(
            suffix=".yaml", prefix=f'{lab_title.replace(" ","_")}_'
        ).name,
        "w",
        encoding="utf-8",
    ) as outfile:
        yaml.dump(yaml.full_load(yaml_string), outfile, default_flow_style=False)

        message = dict(
            toPersonEmail=user_email,
            markdown=f'Your lab "{lab_title}" has been deleted. Attached is the YAML Topology file',
            files=[outfile.name],
        )

        await webex.post_message_to_webex(message)


async def delete_accounts(activity):
    cml_servers = CONFIG.SERVER_LIST.split(",")
    if activity.get("text") == "delete accounts":
        webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
        card_file = "./cards/delete_account_get_password.json"
        with open(f"{card_file}", encoding="utf8") as fp:
            text = fp.read()
        card = json.loads(text)

        # If group then send a DM with a card
        if activity.get("roomType", "") == "group":
            message = dict(
                text="Delete COLAB Accounts",
                toPersonId=activity["sender"],
                attachments=[
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": card,
                    }
                ],
            )
            result = await webex.post_message_to_webex(message)
            message = dict(
                text="I've direct messaged you.",
                roomId=activity["roomId"],
                parentId=activity["parentId"],
                attachments=[],
            )
            await webex.post_message_to_webex(message)
            activity["roomId"] = result.get("roomId", "")
        # if direct, send a card to the same room
        else:
            message = dict(
                text="Delete COLAB Accounts",
                roomId=activity["roomId"],
                attachments=[
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": card,
                    }
                ],
            )
            await webex.post_message_to_webex(message)
        # Post dialogue information to DB
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            dialogue_record = {
                "sender": activity["sender"],
                "sender_email": activity["sender_email"],
                "roomId": activity["roomId"],
                "roomType": activity["roomType"],
                "id": activity["id"],
                "created": activity["created"],
                "dialogue_name": "colab_delete_accounts",
                "dialogue_step": 1,
                "dialogue_max_steps": 2,
                "dialogue_data": [],
                "card_dialogue_index": "colab_delete_accounts",
                "card_feature_index": "colab",
            }
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
                logging.debug(post_id)
            except Exception as e:
                logging.warning(e)
                print("Failed to connect to DB")
        return
    if (
        activity.get("dialogue_name") == "colab_delete_accounts"
        and activity.get("dialogue_step") == 1
    ):
        webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
        # In case a new dialogue has been entered, send msg, and cancel old dialogue
        try:
            if not activity["inputs"]["colab_password"]:
                message = dict(
                    text='Send "help" for available commands',
                    roomId=activity["roomId"],
                    attachments=[],
                )
                await webex.post_message_to_webex(message)
                # Remove dialogue from DB
                with pymongo.MongoClient(mongo_url) as client:
                    db = client[CONFIG.MONGO_DB_ACTIVITY]
                    posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                    query_lab_filter = {
                        "sender": activity["sender"],
                        "roomId": activity["roomId"],
                        "dialogue_name": "colab_delete_accounts",
                    }
                return
        except Exception as e:
            logging.warning(e)
            message = dict(
                text="I thought we were talking about deleting your accounts. Please send a new command",
                roomId=activity["roomId"],
                attachments=[],
            )
            await webex.post_message_to_webex(message)
            # Remove dialogue from DB
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                query_lab_filter = {
                    "sender": activity["sender"],
                    "roomId": activity["roomId"],
                    "dialogue_name": "colab_delete_accounts",
                }
            return

        webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
        message = dict(
            text=bot_wait_message,
            roomId=activity["roomId"],
            attachments=[],
        )
        await webex.post_message_to_webex(message)
        urls_cml_servers = [https_header + s for s in cml_servers]
        if re.search(botId_regex_pattern, CONFIG.BOT_ID):
            id_template = "17"  # prod
        else:
            id_template = "13"  # dev
        url = f"https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/"
        headers = {"Content-Type": content_type}
        user_and_domain = activity["sender_email"].split("@")
        body = {
            "extra_vars": {
                "cml_server_list": urls_cml_servers,
                "colab_user_email": activity["sender_email"],
                "colab_user_username": user_and_domain[0],
                "colab_user_password": activity["inputs"]["colab_password"],
                "vcenter_address": CONFIG.VCENTER_SERVER,
            }
        }
        auth = aiohttp.BasicAuth(
            login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding="utf-8"
        )
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60), auth=auth
        )
        logging.debug("%s %s", logging_message, session)
        try:
            async with session.request(
                method="POST",
                url=url,
                headers=headers,
                data=json.dumps(body),
                ssl=False,
            ) as res:
                if res.status != 201:
                    message = dict(
                        text=awx_server_error_message + str(res.status),
                        roomId=activity["sender_email"],
                        attachments=[],
                    )
                    await webex.post_message_to_webex(message)
                    await session.close()
                else:
                    await session.close()
        except Exception as e:
            logging.warning(e)
            message = dict(
                text=awx_server_error_message + str(res.status),
                roomId=activity["sender_email"],
                attachments=[],
            )
            await webex.post_message_to_webex(message)
            try:
                await session.close()
            except Exception as e5:
                logging.warning(e5)
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            query_lab_filter = {
                "sender": activity["sender"],
                "roomId": activity["roomId"],
                "dialogue_name": "colab_delete_accounts",
            }
            try:
                posts.delete_one(query_lab_filter)
            except Exception as e:
                logging.warning(e)
                print("Failed to connect to DB")


async def bot_delete_accounts(activity):
    webex = WebExClient(webex_bot_token=activity["webex_bot_token"])
    cml_servers = CONFIG.SERVER_LIST.split(",")
    urls_cml_servers = [https_header + s for s in cml_servers]

    if re.search(botId_regex_pattern, CONFIG.BOT_ID):
        id_template = "38"  # prod
    else:
        id_template = "39"  # dev

    url = f"https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/"
    headers = {"Content-Type": content_type}
    user_and_domain = activity["sender_email"].split("@")
    body = {
        "extra_vars": {
            "cml_server_list": urls_cml_servers,
            "colab_user_email": activity["sender_email"],
            "colab_user_username": user_and_domain[0],
            "vcenter_address": CONFIG.VCENTER_SERVER,
            "colab_room_id": CONFIG.AUTHORIZED_ROOMS,
        }
    }
    auth = aiohttp.BasicAuth(
        login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding="utf-8"
    )
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60), auth=auth)
    logging.debug("%s %s", logging_message, session)
    try:
        async with session.request(
            method="POST", url=url, headers=headers, data=json.dumps(body), ssl=False
        ) as res:
            if res.status != 201:
                message = dict(
                    text=awx_server_error_message + str(res.status),
                    roomId=activity["sender_email"],
                    attachments=[],
                )
                await webex.post_message_to_webex(message)
                await session.close()
            else:
                await session.close()
    except Exception as e6:
        logging.warning(e6)
        message = dict(
            text=awx_server_error_message + str(res.status),
            roomId=activity["sender_email"],
            attachments=[],
        )
        await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e:
            logging.warning(e)


async def get_iam_user(iam_username, iam=None):
    if iam is None:
        iam = boto3.resource(
            "iam",
            region_name=CONFIG.AWS_REGION_COLAB,
            aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID_COLAB,
            aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY_COLAB,
        )

    try:
        user = iam.User(iam_username)
    except Exception as e:
        logging.warning(e)
        print(find_user_message)
        return

    return user
