#!/usr/bin/env python
# -*- coding: utf-8 -*-
import aiohttp
import logging
from config import DefaultConfig as CONFIG
from webex import WebExClient
import json
import pymongo
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


mongo_url = 'mongodb://' + CONFIG.MONGO_INITDB_ROOT_USERNAME + ':' + CONFIG.MONGO_INITDB_ROOT_PASSWORD + '@' + CONFIG.MONGO_SERVER + ':' + CONFIG.MONGO_PORT


async def create_accounts(activity):
    cml_servers = CONFIG.SERVER_LIST.split(',')
    webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
    if activity.get('parentId'):
        message = dict(text='Working... This may take a minute or two...',
                       roomId=activity['roomId'],
                       parentId=activity['parentId'],
                       attachments=[])
        r = await webex.post_message_to_webex(message)
    urls_cml_servers = ['https://' + s for s in cml_servers]
    if re.search(r'1MDFmYzc$', CONFIG.BOT_ID):
        id_template = '14'  # prod
    else:
        id_template = '10'  # for dev
    url = f'https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/'
    headers = {'Content-Type': 'application/json'}
    user_and_domain = activity['sender_email'].split('@')
    body = {"extra_vars": {"cml_server_list": urls_cml_servers,
                           "colab_user_email": activity['sender_email'],
                           "colab_user_username": user_and_domain[0],
                           "vcenter_address": CONFIG.VCENTER_SERVER
                           }}
    auth = aiohttp.BasicAuth(login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding='utf-8')
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), auth=auth)
    try:
        async with session.request(method="POST", url=url,
                                   headers=headers, data=json.dumps(body), ssl=False) as res:
            if res.status != 201:
                if activity.get('parentId'):
                    message = dict(text='Error contacting AWX server. ' + str(res.status),
                                   roomId=activity['roomId'],
                                   parentId=activity['parentId'],
                                   attachments=[])
                else:
                    message = dict(text='Error contacting AWX server. ' + str(res.status),
                                   roomId=activity['roomId'],
                                   attachments=[])
                r = await webex.post_message_to_webex(message)
                await session.close()
    except Exception as e:
        logging.warning(e)
        if activity.get('parentId'):
            message = dict(text='Error contacting AWX server. ' + str(res.status),
                           roomId=activity['roomId'],
                           parentId=activity['parentId'],
                           attachments=[])
        else:
            message = dict(text='Error contacting AWX server. ' + str(res.status),
                           roomId=activity['roomId'],
                           attachments=[])
        r = await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e:
            logging.warning(e)
    return


async def create_aws_account(activity):
    cml_servers = CONFIG.SERVER_LIST.split(',')
    webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
    message = dict(text='Working... This may take a minute or two...',
                   roomId=activity['roomId'],
                   parentId=activity['parentId'],
                   attachments=[])
    r = await webex.post_message_to_webex(message)
    urls_cml_servers = ['https://' + s for s in cml_servers]
    if re.search(r'1MDFmYzc$', CONFIG.BOT_ID):
        id_template = '15'  # prod
    else:
        id_template = '11'  # for dev
    url = f'https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/'
    headers = {'Content-Type': 'application/json'}
    user_and_domain = activity['sender_email'].split('@')
    body = {"extra_vars": {"cml_server_list": urls_cml_servers,
                           "colab_user_email": activity['sender_email'],
                           "colab_user_username": user_and_domain[0],
                           "vcenter_address": CONFIG.VCENTER_SERVER
                           }}
    auth = aiohttp.BasicAuth(login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding='utf-8')
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), auth=auth)
    try:
        async with session.request(method="POST", url=url,
                                   headers=headers, data=json.dumps(body), ssl=False) as res:
            if res.status != 201:
                message = dict(text='Error contacting AWX server. ' + str(res.status),
                               roomId=activity['roomId'],
                               parentId=activity['parentId'],
                               attachments=[])
                r = await webex.post_message_to_webex(message)
                await session.close()
    except Exception as e:
        logging.warning(e)
        message = dict(text='Error contacting AWX server. ' + str(res.status),
                       roomId=activity['roomId'],
                       parentId=activity['parentId'],
                       attachments=[])
        r = await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e:
            logging.warning(e)
    return


async def create_vpn_account(activity):
    cml_servers = CONFIG.SERVER_LIST.split(',')
    webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
    message = dict(text='Working... This may take a minute or two...',
                   roomId=activity['roomId'],
                   parentId=activity['parentId'],
                   attachments=[])
    r = await webex.post_message_to_webex(message)
    urls_cml_servers = ['https://' + s for s in cml_servers]
    if re.search(r'1MDFmYzc$', CONFIG.BOT_ID):
        id_template = '16'  # prod
    else:
        id_template = '12'  # for dev
    url = f'https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/'
    headers = {'Content-Type': 'application/json'}
    user_and_domain = activity['sender_email'].split('@')
    body = {"extra_vars": {"cml_server_list": urls_cml_servers,
                           "colab_user_email": activity['sender_email'],
                           "colab_user_username": user_and_domain[0],
                           "vcenter_address": CONFIG.VCENTER_SERVER
                           }}
    auth = aiohttp.BasicAuth(login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding='utf-8')
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), auth=auth)
    try:
        async with session.request(method="POST", url=url,
                                   headers=headers, data=json.dumps(body), ssl=False) as res:
            if res.status != 201:
                message = dict(text='Error contacting AWX server. ' + str(res.status),
                               roomId=activity['roomId'],
                               parentId=activity['parentId'],
                               attachments=[])
                r = await webex.post_message_to_webex(message)
                await session.close()
    except Exception as e:
        logging.warning(e)
        message = dict(text='Error contacting AWX server. ' + str(res.status),
                       roomId=activity['roomId'],
                       parentId=activity['parentId'],
                       attachments=[])
        r = await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e:
            logging.warning(e)
    return


async def delete_accounts(activity):
    cml_servers = CONFIG.SERVER_LIST.split(',')
    if activity.get('text') == 'delete accounts':
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        card_file = './cards/delete_account_get_password.json'
        with open(f'{card_file}') as fp:
            text = fp.read()
        card = json.loads(text)

        # If group then send a DM with a card
        if activity.get('roomType', '') == 'group':
            message = dict(text='Delete COLAB Accounts',
                           toPersonId=activity['sender'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            result = await webex.post_message_to_webex(message)
            message = dict(text="I've direct messaged you.",
                           roomId=activity['roomId'],
                           parentId=activity['parentId'],
                           attachments=[])
            r = await webex.post_message_to_webex(message)
            activity['roomId'] = result.get('roomId', '')
        # if direct, send a card to the same room
        else:
            message = dict(text='Delete COLAB Accounts',
                           roomId=activity['roomId'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            r = await webex.post_message_to_webex(message)
        # Post dialogue information to DB
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            dialogue_record = {'sender': activity['sender'],
                               'sender_email': activity['sender_email'],
                               'roomId': activity['roomId'],
                               'roomType': activity['roomType'],
                               'id': activity['id'],
                               'created': activity['created'],
                               'dialogue_name': 'colab_delete_accounts',
                               'dialogue_step': 1,
                               'dialogue_max_steps': 2,
                               'dialogue_data': [],
                               'card_dialogue_index': 'colab_delete_accounts',
                               'card_feature_index': 'colab'}
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
            except Exception as e:
                logging.warning(e)
                print('Failed to connect to DB')
        return
    if activity.get('dialogue_name') == 'colab_delete_accounts' and activity.get('dialogue_step') == 1:
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        # In case a new dialogue has been entered, send msg, and cancel old dialogue
        try:
            if not activity['inputs']['colab_password']:
                message = dict(text='Send "help" for available commands',
                               roomId=activity['roomId'],
                               attachments=[])
                r = await webex.post_message_to_webex(message)
                # Remove dialogue from DB
                with pymongo.MongoClient(mongo_url) as client:
                    db = client[CONFIG.MONGO_DB_ACTIVITY]
                    posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                    query_lab_filter = {'sender': activity['sender'],
                                        'roomId': activity['roomId'],
                                        'dialogue_name': 'colab_delete_accounts'}
                return
        except Exception as e:
            logging.warning(e)
            message = dict(text='I thought we were talking about deleting your accounts. Please send a new command',
                           roomId=activity['roomId'],
                           attachments=[])
            r = await webex.post_message_to_webex(message)
            # Remove dialogue from DB
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                query_lab_filter = {'sender': activity['sender'],
                                    'roomId': activity['roomId'],
                                    'dialogue_name': 'colab_delete_accounts'}
            return

        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text='Working, this may take a minute or two...',
                       roomId=activity['roomId'],
                       attachments=[])
        r = await webex.post_message_to_webex(message)
        urls_cml_servers = ['https://' + s for s in cml_servers]
        if re.search(r'1MDFmYzc$', CONFIG.BOT_ID):
            id_template = '17'  # prod
        else:
            id_template = '13'  # dev
        url = f'https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/'
        headers = {'Content-Type': 'application/json'}
        user_and_domain = activity['sender_email'].split('@')
        body = {"extra_vars": {"cml_server_list": urls_cml_servers,
                               "colab_user_email": activity['sender_email'],
                               "colab_user_username": user_and_domain[0],
                               "colab_user_password": activity['inputs']['colab_password'],
                               "vcenter_address": CONFIG.VCENTER_SERVER
                               }}
        auth = aiohttp.BasicAuth(login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding='utf-8')
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), auth=auth)
        try:
            async with session.request(method="POST", url=url,
                                       headers=headers, data=json.dumps(body), ssl=False) as res:
                if res.status != 201:
                    message = dict(text='Error contacting AWX server. ' + str(res.status),
                                   roomId=activity['sender_email'],
                                   attachments=[])
                    r = await webex.post_message_to_webex(message)
                    await session.close()
        except Exception as e:
            logging.warning(e)
            message = dict(text='Error contacting AWX server. ' + str(res.status),
                           roomId=activity['sender_email'],
                           attachments=[])
            r = await webex.post_message_to_webex(message)
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            query_lab_filter = {'sender': activity['sender'],
                                'roomId': activity['roomId'],
                                'dialogue_name': 'colab_delete_accounts'}
            try:
                posts.delete_one(query_lab_filter)
            except Exception as e:
                logging.warning(e)
                print('Failed to connect to DB')

    return


async def create_gitlab(activity):
    webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
    message = dict(text='Working... This can take up to 10 minutes...',
                   roomId=activity['roomId'],
                   parentId=activity['parentId'],
                   attachments=[])
    r = await webex.post_message_to_webex(message)
    if re.search(r'1MDFmYzc$', CONFIG.BOT_ID):
        id_template = '18'  # prod
    else:
        id_template = '19'  # for dev
    url = f'https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/'
    headers = {'Content-Type': 'application/json'}
    user_and_domain = activity['sender_email'].split('@')
    body = {"extra_vars": {"colab_user_username": user_and_domain[0],
                           "colab_user_email": activity['sender_email']}}
    auth = aiohttp.BasicAuth(login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding='utf-8')
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), auth=auth)
    try:
        async with session.request(method="POST", url=url,
                                   headers=headers, data=json.dumps(body), ssl=False) as res:
            if res.status != 201:
                message = dict(text='Error contacting AWX server. ' + str(res.status),
                               roomId=activity['roomId'],
                               parentId=activity['parentId'],
                               attachments=[])
                r = await webex.post_message_to_webex(message)
                await session.close()
    except Exception as e:
        logging.warning(e)
        message = dict(text='Error contacting AWX server. ' + str(res.status),
                       roomId=activity['roomId'],
                       parentId=activity['parentId'],
                       attachments=[])
        r = await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e:
            logging.warning(e)
    return


async def remove_gitlab(activity):
    webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
    message = dict(text='Working... This can take up to 5 minutes...',
                   roomId=activity['roomId'],
                   parentId=activity['parentId'],
                   attachments=[])
    r = await webex.post_message_to_webex(message)
    if re.search(r'1MDFmYzc$', CONFIG.BOT_ID):
        id_template = '20'  # prod
    else:
        id_template = '21'  # for dev
    url = f'https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/'
    headers = {'Content-Type': 'application/json'}
    user_and_domain = activity['sender_email'].split('@')
    body = {"extra_vars": {"colab_user_username": user_and_domain[0],
                           "colab_user_email": activity['sender_email']}}
    auth = aiohttp.BasicAuth(login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding='utf-8')
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), auth=auth)
    try:
        async with session.request(method="POST", url=url,
                                   headers=headers, data=json.dumps(body), ssl=False) as res:
            if res.status != 201:
                message = dict(text='Error contacting AWX server. ' + str(res.status),
                               roomId=activity['roomId'],
                               parentId=activity['parentId'],
                               attachments=[])
                r = await webex.post_message_to_webex(message)
                await session.close()
    except Exception as e:
        logging.warning(e)
        message = dict(text='Error contacting AWX server. ' + str(res.status),
                       roomId=activity['roomId'],
                       parentId=activity['parentId'],
                       attachments=[])
        r = await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e:
            logging.warning(e)
    return


async def extend_gitlab(activity):
    webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
    message = dict(text='Working... This can take a minute...',
                   roomId=activity['roomId'],
                   parentId=activity['parentId'],
                   attachments=[])
    r = await webex.post_message_to_webex(message)

    id_template = '37'  # prod only or both prod and dev will increase counters

    url = f'https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/'
    headers = {'Content-Type': 'application/json'}
    user_and_domain = activity['sender_email'].split('@')
    body = {"extra_vars": {"colab_user_username": user_and_domain[0],
                           "colab_user_email": activity['sender_email']}}
    auth = aiohttp.BasicAuth(login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding='utf-8')
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), auth=auth)
    try:
        async with session.request(method="POST", url=url,
                                   headers=headers, data=json.dumps(body), ssl=False) as res:
            if res.status != 201:
                message = dict(text='Error contacting AWX server. ' + str(res.status),
                               roomId=activity['roomId'],
                               parentId=activity['parentId'],
                               attachments=[])
                r = await webex.post_message_to_webex(message)
                await session.close()
    except Exception as e:
        logging.warning(e)
        message = dict(text='Error contacting AWX server. ' + str(res.status),
                       roomId=activity['roomId'],
                       parentId=activity['parentId'],
                       attachments=[])
        r = await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e:
            logging.warning(e)
    return


async def bot_delete_accounts(activity):
    webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
    cml_servers = CONFIG.SERVER_LIST.split(',')
    urls_cml_servers = ['https://' + s for s in cml_servers]

    if re.search(r'1MDFmYzc$', CONFIG.BOT_ID):
        id_template = '38'  # prod
    else:
        id_template = '39'  # dev

    url = f'https://{CONFIG.AWX_SERVER}/api/v2/job_templates/{id_template}/launch/'
    headers = {'Content-Type': 'application/json'}
    user_and_domain = activity['sender_email'].split('@')
    body = {"extra_vars": {"cml_server_list": urls_cml_servers,
                           "colab_user_email": activity['sender_email'],
                           "colab_user_username": user_and_domain[0],
                           "vcenter_address": CONFIG.VCENTER_SERVER,
                           "colab_room_id": CONFIG.AUTHORIZED_ROOMS,
                           }}
    auth = aiohttp.BasicAuth(login=CONFIG.AWX_USERNAME, password=CONFIG.AWX_PASSWORD, encoding='utf-8')
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), auth=auth)
    try:
        async with session.request(method="POST", url=url,
                                   headers=headers, data=json.dumps(body), ssl=False) as res:
            if res.status != 201:
                message = dict(text='Error contacting AWX server. ' + str(res.status),
                               roomId=activity['sender_email'],
                               attachments=[])
                r = await webex.post_message_to_webex(message)
                await session.close()
    except Exception as e:
        logging.warning(e)
        message = dict(text='Error contacting AWX server. ' + str(res.status),
                       roomId=activity['sender_email'],
                       attachments=[])
        r = await webex.post_message_to_webex(message)
        try:
            await session.close()
        except Exception as e:
            logging.warning(e)
    return

