from .CML import CML
from features.catch_all import catch_all
from config import DefaultConfig as CONFIG
from webex import WebExClient
import json
import pymongo
from jinja2 import Template
import logging

mongo_url = 'mongodb://' + CONFIG.MONGO_INITDB_ROOT_USERNAME + ':' + CONFIG.MONGO_INITDB_ROOT_PASSWORD + '@' + CONFIG.MONGO_SERVER + ':' + CONFIG.MONGO_PORT


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

        servers_for_card = ''
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
                                   'dialogue_max_steps': 2,
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
        results_message = ''
        # for cml_server in cml_servers:
        # try:
        #     if activity['inputs']:
        return
    # WIP
