from .CML import CML
from config import DefaultConfig as CONFIG
from webex import WebExClient
import json
import pymongo
from jinja2 import Template
import logging
import boto3


mongo_url = 'mongodb://' + CONFIG.MONGO_INITDB_ROOT_USERNAME + ':' + CONFIG.MONGO_INITDB_ROOT_PASSWORD + '@' + CONFIG.MONGO_SERVER + ':' + CONFIG.MONGO_PORT


async def dynamo_download_items(table: str) -> list:
    items = list()
    try:
        dynamodb = boto3.resource('dynamodb',
                                  region_name=CONFIG.AWS_REGION,
                                  aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY)
        table = dynamodb.Table(table)
        response = table.scan()
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        return items
    except Exception as e:
        logging.error(e)
        return items


async def administrator_check(activity):
    if activity.get('sender_email') in CONFIG.ADMINISTRATORS.split(','):
        return True
    else:
        return False


async def webex_not_admin(activity):
    webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
    message = dict(text="Sorry. I don't see your name on the COLAB administrators list '&#x1F641;'",
                   roomId=activity['roomId'],
                   attachments=[])
    await webex.post_message_to_webex(message)


async def admin_in_group_room(activity):
    if activity.get('roomType', '') == 'group':
        return True
    else:
        return False


async def webex_admin_in_group_room(activity):
    webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
    message = dict(text="Please direct message me with admin requests",
                   roomId=activity['roomId'],
                   attachments=[])
    await webex.post_message_to_webex(message)


async def admin_alert_cml_users(activity):
    # generate cards server choices
    cml_servers = CONFIG.SERVER_LIST.split(',')
    if activity.get('text') == 'admin alert cml users':
        if not await administrator_check(activity):
            await webex_not_admin(activity)
            return
        if await admin_in_group_room(activity):
            await webex_admin_in_group_room(activity)
            return

        if cml_servers:
            lab_choices_string = '{"type": "Input.ChoiceSet","id": "CML servers","style": "expanded","value": "1","choices": ['
            for i in cml_servers:
                lab_choices_string += '{"title": "' + i + '","value": "' + i + '"},'
            servers_for_card = lab_choices_string[:-1]
            servers_for_card += '],"isMultiSelect": true},'

            # send card with cml servers as check boxes
            webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
            card_file = './cards/cml_server_users_server_choices.json'
            with open(f'{card_file}') as file_:
                template = Template(file_.read())
            card = template.render(server_choices=servers_for_card)
            card_json = json.loads(card)
            message = dict(text='CML alert users server choices',
                           roomId=activity['roomId'],
                           attachments=[
                               {'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card_json}])
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
                                   'dialogue_name': 'cml_alert_server_choices',
                                   'dialogue_step': 1,
                                   'dialogue_max_steps': 3,
                                   'dialogue_data': [],
                                   'card_dialogue_index': 'cml_alert_server_choices',
                                   'card_feature_index': 'cml_alert'}
                try:
                    post_id = posts.insert_one(dialogue_record).inserted_id
                except Exception as e:
                    logging.warning('Failed to connect to DB')
                    logging.warning(e)
        return

    if activity.get('dialogue_name') == 'cml_alert_server_choices' and activity.get('dialogue_step') == 1:
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        if activity.get('inputs').get('CML servers'):
            servers = activity['inputs']['CML servers'].split(',')
            message = dict(
                text=f'What would you like to tell the users of servers: {", ".join(servers)}?',
                roomId=activity['roomId'],
                attachments=[])
            await webex.post_message_to_webex(message)
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                try:
                    doc = posts.find_one_and_update(
                        {'id': activity['id']},
                        {'$set': {'dialogue_step': 2,
                                  'card_dialogue_index': 'cml_alert_server_choices',
                                  'dialogue_data': {'cml_servers': servers},
                                  }
                         }
                    )
                except Exception as e:
                    logging.warning('Failed to connect to DB')
                    logging.warning(e)
        else:
            message = dict(text="I thought we were talking about admin alerting cml users. Let's start over.",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            # Delete the dialogue record
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                query_lab_filter = {'sender': activity['sender'],
                                    'roomId': activity['roomId'],
                                    'dialogue_name': 'cml_alert_server_choices'}
                try:
                    r = posts.delete_one(query_lab_filter)
                except Exception as e:
                    logging.warning('Failed to connect to DB')
                    logging.warning(e)
    if activity.get('dialogue_name') == 'cml_alert_server_choices' and activity.get('dialogue_step') == 2:
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        if activity.get('original_text'):
            message = f"\n\nIs the below the message you would like to send **(yes/no)**? : \n\n  - {activity.get('original_text')}"
            message = dict(
                text=message,
                roomId=activity['roomId'],
                attachments=[])
            await webex.post_message_to_webex(message)
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                try:
                    dialogue_data = activity.get('dialogue_data')
                    dialogue_data['text'] = activity.get('original_text')
                    doc = posts.find_one_and_update(
                        {'id': activity['id']},
                        {'$set': {'dialogue_step': 3,
                                  'card_dialogue_index': 'cml_alert_server_choices',
                                  'dialogue_data': dialogue_data
                                  }
                         }
                    )
                except Exception as e:
                    logging.warning('Failed to connect to DB')
                    logging.warning(e)
    if activity.get('dialogue_name') == 'cml_alert_server_choices' and activity.get('dialogue_step') == 3:
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        if activity.get('text') == 'no':
            message = f"Ok - Let me know if I can help"
            message = dict(
                text=message,
                roomId=activity['roomId'],
                attachments=[])
            await webex.post_message_to_webex(message)
        if activity.get('text') == 'yes':
            records = await dynamo_download_items('colab_directory')
            # New directory with username as key and email as value
            new_directory = dict()
            for i in records:
                new_directory[i['username']] = i['email']
            for server in activity['dialogue_data']['cml_servers']:
                cml = CML(CONFIG.CML_USERNAME, CONFIG.CML_PASSWORD, server)
                mentions = list()
                if not await cml.get_token():
                    message = dict(text='Error accessing server ' + server + ': ' + str(
                        cml.status_code) + ' ' + str(cml.bearer_token),
                                   roomId=activity['roomId'],
                                   parentId=activity['parentId'],
                                   attachments=[])
                    await webex.post_message_to_webex(message)
                    # continue
                else:
                    if not await cml.get_diagnostics():
                        message = dict(
                            text='***' + server + '*** Error retrieving diagnostics: ' + str(cml.diagnostics),
                            roomId=activity['roomId'],
                            parentId=activity['parentId'],
                            attachments=[])
                        await webex.post_message_to_webex(message)
                        # continue
                    else:
                        for k, v in cml.diagnostics['user_roles']['labs_by_user'].items():
                            if v:
                                if new_directory.get(k):
                                    mentions.append(f'<@personEmail:{new_directory.get(k)}|{k}>')
                if mentions:
                    message_text = f"The following is an **important message** for users of {server}: \n\n  - {activity['dialogue_data']['text']} \n\n{' '.join(mentions)}"
                else:
                    message_text = f"The following is an **important message** for users of {server}: \n\n  - {activity['dialogue_data']['text']} \n\n"
                logging.info(message_text)
                message = dict(
                    text=message_text,
                    roomId=CONFIG.AUTHORIZED_ROOMS,
                    attachments=[])
                await webex.post_message_to_webex(message)

        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            query_lab_filter = {'sender': activity['sender'],
                                'roomId': activity['roomId'],
                                'dialogue_name': 'cml_alert_server_choices'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                logging.warning('Failed to connect to DB')
                logging.warning(e)
    return
