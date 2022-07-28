#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
import re
import aiohttp
import pymongo
import urllib3
import boto3
from config import DefaultConfig as CONFIG
from webex import WebExClient


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging_message = "This is the aiohttp Client session"
bot_wait_message = "This may take a minute or two..."
https_header = "https://"
botId_regex_pattern = r"1MDFmYzc$"
content_type = "application/json"
awx_server_error_message = "Error contacting AWX server. "

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
    iam = boto3.resource("iam", AWS_ACCESS_KEY_ID=CONFIG.AWS_ACCESS_KEY_ID_COLAB, AWS_SECRET_ACCESS_KEY=CONFIG.AWS_SECRET_ACCESS_KEY_COLAB)

    user_and_domain = activity["sender_email"].split("@")
    iam_username = user_and_domain[0]
    logging.debug(iam_username)
    try:
        user = iam.User(iam_username)
        access_key_iterator = user.access_keys.all()
        access_key_count = 0
        for _ in access_key_iterator:
            access_key_count += 1
    except Exception as e:
        logging.warning(e)
        print("Cannot find user")
        return

    # If the user has active access keys that colabot has not expired, don't create keys
    if access_key_count > 0:
        message = dict(
            text=(
                "You already have active aws key(s),"
                + " if you would like to refresh them, use **reset aws keys**"
            ),
            toPersonId=activity["sender"],
        )
        await webex.post_message_to_webex(message)
        return

    if access_key_count == 0:
        await create_key_and_message_user(activity, user, webex)


async def create_key_and_message_user(activity, user, webex):
    access_key_pair = user.create_access_key_pair()
    new_access_key_id = access_key_pair.access_key_id
    new_secret_access_key = access_key_pair.secret_access_key

    key_message = new_access_key_id + new_secret_access_key

    message = dict(
        text=(
            "Access key created: \n"
            + f"- Access Key id: test id \n"
            + f"- Access Key secret: test secret "
            + "Remember **not to share** your access key id or secret"
        ),
        toPersonId=activity["sender"],
    )

    logging.debug("Sending message to %s", activity["sender"])
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
