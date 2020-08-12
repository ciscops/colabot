#!/usr/bin/env python
# -*- coding: utf-8 -*-
import aiohttp
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
    message = dict(text='Working... This may take a minute or two...',
                   roomId=activity['roomId'],
                   attachments=[])
    await webex.post_message_to_webex(message)
    urls_cml_servers = ['https://' + s for s in cml_servers]
    if re.search(r'1MDFmYzc$', CONFIG.BOT_ID):
        id_template = '29'  # prod
    else:
        id_template = '27'  # for dev
    url = f'https://cpn-rtp-awx1.colab.ciscops.net/api/v2/job_templates/{id_template}/launch/'
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
                               attachments=[])
                await webex.post_message_to_webex(message)
                await session.close()
    except Exception as e:
        message = dict(text='Error contacting AWX server. ' + str(res.status),
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        try:
            await session.close()
        except:
            pass
    return {'status_code': 200}


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
                           attachments=[])
            await webex.post_message_to_webex(message)
            activity['roomId'] = result.get('roomId', '')
        # if direct, send a card to the same room
        else:
            message = dict(text='Delete COLAB Accounts',
                           roomId=activity['roomId'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            await webex.post_message_to_webex(message)
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
                print('Failed to connect to DB')
        return {'status_code': 200}
    if activity.get('dialogue_name') == 'colab_delete_accounts' and activity.get('dialogue_step') == 1:
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        # In case a new dialogue has been entered, send msg, and cancel old dialogue
        try:
            if not activity['inputs']['colab_password']:
                message = dict(text='Send "help" for available commands',
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                # Remove dialogue from DB
                with pymongo.MongoClient(mongo_url) as client:
                    db = client[CONFIG.MONGO_DB_ACTIVITY]
                    posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                    query_lab_filter = {'sender': activity['sender'],
                                        'roomId': activity['roomId'],
                                        'dialogue_name': 'colab_delete_accounts'}
                return {'status_code': 200}
        except Exception:
            message = dict(text='I thought we were talking about deleting your accounts. Please send a new command',
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            # Remove dialogue from DB
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                query_lab_filter = {'sender': activity['sender'],
                                    'roomId': activity['roomId'],
                                    'dialogue_name': 'colab_delete_accounts'}
            return {'status_code': 200}

        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text='Working, this may take a minute or two...',
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        urls_cml_servers = ['https://' + s for s in cml_servers]
        if re.search(r'1MDFmYzc$', CONFIG.BOT_ID):
            id_template = '30'  # prod
        else:
            id_template = '28'  # dev
        url = f'https://cpn-rtp-awx1.colab.ciscops.net/api/v2/job_templates/{id_template}/launch/'
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
                    await webex.post_message_to_webex(message)
                    await session.close()
        except Exception as e:
            message = dict(text='Error contacting AWX server. ' + str(res.status),
                           roomId=activity['sender_email'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            try:
                await session.close()
            except:
                pass
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            query_lab_filter = {'sender': activity['sender'],
                                'roomId': activity['roomId'],
                                'dialogue_name': 'colab_delete_accounts'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                print('Failed to connect to DB')

    return {'status_code': 200}
