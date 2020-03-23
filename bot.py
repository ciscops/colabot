#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp.web_request import Request
from aiohttp.web_response import Response
from features.VIRL_chat import virl_chat
import hashlib
import hmac
import json
from webex import WebExClient
from config import DefaultConfig as CONFIG
import pymongo
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

mongo_url = 'mongodb://' + CONFIG.MONGO_INITDB_ROOT_USERNAME + ':' + CONFIG.MONGO_INITDB_ROOT_PASSWORD + '@' + CONFIG.MONGO_SERVER + ':' + CONFIG.MONGO_PORT

help_menu_list = ['**VIRL create account** > create account\n',
                  '**VIRL delete account** > delete account\n',
                  '**VIRL delete lab** > delete lab\n',
                  '**VIRL list all labs** > list all labs\n',
                  '**VIRL list my lab details** > list your labs with details\n',
                  '**VIRL list my labs** > list only your labs\n',
                  '**VIRL list users** > list users\n',
                  '**VIRL reset password** > reset password\n',
                  '**VIRL show server utilization** > show current CPU and Memory usage\n',
                  '**VIRL stop lab** > stop labs or your choice\n',
                  '**help** > display available commands\n']


class COLABot:
    """
    WebEx
    """
    def __init__(self, webex_bot_token=None, webex_client_signing_secret=None):
        self.webex_client = WebExClient(webex_bot_token=webex_bot_token)
        self.webex_client_signing_secret = webex_client_signing_secret
        self.webex_bot_token = webex_bot_token
        self.activity = None

    async def process(self, req: Request):
        """
        Accepts an incoming webhook request and converts it to an Activity which can be processed by the bot's logic.
        i.e., Adapts WebEx to Bot logic
        """
        # Check WebEx WebHook SECRET
        if not self.webex_client_signing_secret:
            warning = (
                "\n****************************************************************************************\n"
                "* WARNING: Your bot is operating without recommended security mechanisms in place.       *\n"
                "* Initialize your adapter and your WebEx Webhook with a SECRET for payload signature     *\n"
                "******************************************************************************************\n"
            )
            raise Exception(warning + "Required: include a clientSigningSecret to verify incoming Events API webhooks")
        else:
            body = await req.read()
            print('This is the initial message')
            print(body)
            key_bytes = self.webex_client_signing_secret.encode()
            hashed = hmac.new(key_bytes, body, hashlib.sha1)
            body_signature = hashed.hexdigest()
            print('This is from digest sent in the webhook header: ' + req.headers['X-Spark-Signature'])
            print('This is the resulting digest from hashing the webhook body with the local secret: ' + body_signature)
            if req.headers['X-Spark-Signature'] != body_signature:
                return {'status_code': 403}

        # Process web request
        if not req:
            raise Exception("Request is required")
        body = await req.text()
        if not body:
            raise Exception("Error receiving request body")
        request_dict = json.loads(body)
        if request_dict['resource'] == 'memberships' and request_dict['event'] == 'deleted' and request_dict['data'][
                'personId'] == CONFIG.BOT_ID:
            return {'status_code': 200}
        if request_dict['resource'] == 'messages' and request_dict['event'] == 'created' and request_dict['data'][
                'personId'] == CONFIG.BOT_ID:
            return {'status_code': 200}

        # Create activity from webhook
        self.activity = await self.translate_request_to_activity(request_dict)
        # Apply any security checks, i.e., domain name, room name, etc...
        if (self.activity.get('sender_email')) and (self.activity.get('sender') != CONFIG.BOT_ID) \
                and (self.activity.get('resource') == 'messages') and (self.activity.get('event') == 'created'):
            domain = self.activity.get('sender_email').split('@')
            approved_domains = CONFIG.APPROVED_ORG_DOMAINS.split(',')
            if domain[1] not in approved_domains:
                return {'status_code': 403}

        # Check activity for active dialogue. If active, apply saved dialogue data to activity
        if not self.activity:
            return {'status_code': 400}
        else:
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                query_lab_filter = {'sender': self.activity.get('sender'),
                                    'roomId': self.activity.get('roomId')}
                try:
                    result = posts.find_one(query_lab_filter)  # Q: Is this lab already in DB?
                except Exception as e:
                    print('Failed to connect to DB')
                    print(e)
                    return {'status_code': 500}

                # Check if dialogue record is too old, delete it
                pattern = '%Y-%m-%dT%H:%M:%S.%fZ'
                if result:
                    epoch_time_now = time.time()
                    last_dialogue_epoch_time = int(time.mktime(time.strptime(result['created'], pattern)))
                    if epoch_time_now - last_dialogue_epoch_time >= int(CONFIG.DIALOGUE_TIMEOUT):  # Remove any conversations over X seconds
                        try:
                            r = posts.delete_many(query_lab_filter)
                        except Exception as e:
                            print('Could not remove stale dialogue record from DB')
                            print(e)
                            return {'status_code': 500}
                # If somehow the dialogue_max_step is maxed out
                    elif result['dialogue_step'] > result['dialogue_max_steps']:
                        try:
                            r = posts.delete_many(query_lab_filter)
                        except Exception as e:
                            print('Could not remove stale dialogue record from DB')
                            print(e)
                            return {'status_code': 500}
                # Update the activity record with the dialogue fields
                    else:
                        self.activity['sender'] = result.get('sender', '')
                        self.activity['sender_email'] = result.get('sender_email', '')
                        self.activity['roomId'] = result.get('roomId', '')
                        self.activity['roomType'] = result.get('roomType', '')
                        self.activity['id'] = result.get('id', '')
                        self.activity['created'] = result.get('created', '')
                        self.activity['dialogue_name'] = result.get('dialogue_name', '')
                        self.activity['dialogue_step'] = result.get('dialogue_step', '')
                        self.activity['dialogue_max_steps'] = result.get('dialogue_max_steps', '')
                        self.activity['dialogue_data'] = result.get('dialogue_data', '')
                        self.activity['card_dialogue_index'] = result.get('card_dialogue_index', '')
                        self.activity['card_feature_index'] = result.get('card_feature_index', '')
                        self.activity['virl_password'] = result.get('virl_password', '')

            print('\n')
            print('This is the fully populated activity')
            print(self.activity)
            print('\n')

            if self.activity['description'] == 'bot_added':
                await self.bot_added()

            elif self.activity['description'] == 'card_details':
                if self.activity['inputs']['card_feature_index'] == 'virl':
                    result = await virl_chat(self.activity)
                    print(result['status_code'])

            elif self.activity['description'] == 'message_details':
                # This will remove bot name from text if message was "at mention" to the bot
                if self.activity.get('roomType', '') == 'group':
                    self.activity['text'] = self.activity.get('text').replace(self.activity.get('bot_name') + ' ', '')

                # Main Message Activities
                if self.activity.get('text').lower() == 'help':
                    await self.display_help_menu()

                elif self.activity.get('text')[:4] == 'VIRL':  # Add searches for virl dialogue here
                    result = await virl_chat(self.activity)
                    print(result.get('status_code'))

                else:
                    await self.catch_all()
            return {'status_code': 200}

    async def display_help_menu(self):
        message = dict(text=self.generate_help_menu_markdown(help_menu_list),
                       roomId=self.activity['roomId'],
                       attachments=[])
        response = await self.webex_client.post_message_to_webex(message)
        return response

    async def catch_all(self):
        # Below is the catch all for unrecognized commands
        if self.activity.get('description') == 'card_details':
            message = dict(text='The card is inactive. Please generate a new one.',
                           roomId=self.activity['roomId'],
                           attachments=[])
            response = await self.webex_client.post_message_to_webex(message)
            return response
        elif self.activity.get('roomType') == 'group':
            message = dict(text='"' + self.activity['text'] + '?"' + " I'm sorry. I don't understand. Please reply " + "**@" + self.activity['bot_name'] + " help** to see my available commands",
                           roomId=self.activity['roomId'],
                           attachments=[])
            response = await self.webex_client.post_message_to_webex(message)
            return response
        else:
            message = dict(text='"' + self.activity['text'] + '?"' + " I'm sorry. I don't understand. Please reply 'help' to see my available commands",
                           roomId=self.activity['roomId'],
                           attachments=[])
            response = await self.webex_client.post_message_to_webex(message)
            return response

    async def translate_request_to_activity(self, request_dict):
        activity = None
        if request_dict['resource'] == 'memberships' and request_dict['event'] == 'created' and request_dict['data'][
                'personId'] == CONFIG.BOT_ID:
            activity = {'id': request_dict['data']['id'],
                        'resource': request_dict['resource'],
                        'event': request_dict['event'],
                        'sender': request_dict['data']['personId'],
                        'roomId': request_dict['data']['roomId'],
                        'created': request_dict['data']['created'],
                        'roomType': request_dict['data']['roomType'],
                        'description': 'bot_added',
                        'bot_name': CONFIG.BOT_NAME,
                        'webex_bot_token': self.webex_bot_token}

        elif request_dict['resource'] == 'attachmentActions' and request_dict['event'] == 'created':
            message_body = await self.webex_client.get_card_attachment(request_dict['data']['id'])
            activity = {'id': request_dict['data']['id'],
                        'resource': request_dict['resource'],
                        'event': request_dict['event'],
                        'type': request_dict['data']['type'],
                        'sender': request_dict['data']['personId'],
                        'roomId': request_dict['data']['roomId'],
                        'created': request_dict['data']['created'],
                        'inputs': message_body['inputs'],
                        'description': 'card_details',
                        'bot_name': CONFIG.BOT_NAME,
                        'webex_bot_token': self.webex_bot_token}

        elif request_dict['resource'] == 'messages' and request_dict['event'] == 'created' and request_dict['data'][
                'personId'] != CONFIG.BOT_ID:
            message_body = await self.webex_client.get_message_details(request_dict['data']['id'])
            activity = {'id': request_dict['data'].get('id', ''),
                        'roomId': request_dict['data'].get('roomId', ''),
                        'roomType': request_dict['data'].get('roomType', ''),
                        'sender': message_body.get('personId', ''),
                        'sender_email': message_body.get('personEmail', ''),
                        'mentionedPeople': message_body.get('mentionedPeople', ''),
                        'resource': request_dict.get('resource', ''),
                        'event': request_dict.get('event', ''),
                        'created': message_body.get('created', ''),
                        'text': message_body.get('text', ''),
                        'html': message_body.get('html', ''),
                        'description': 'message_details',
                        'bot_name': CONFIG.BOT_NAME,
                        'webex_bot_token': self.webex_bot_token}

        return activity

    async def bot_added(self):
        text = self.generate_help_menu_markdown(help_menu_list)
        message = dict(text=text,
                       roomId=self.activity.get('roomId'),
                       attachments=[])
        response = await self.webex_client.post_message_to_webex(message)
        return response

    def generate_help_menu_markdown(self, help_menu):
        if self.activity['roomType'] == 'group':
            markdown = 'Hi, See my available commands below: \n'
            for i in help_menu:
                markdown += ' - ' + '**' + '@' + self.activity['bot_name'] + '** ' + i
            return markdown
        else:
            markdown = 'Hi, See my available commands below: \n'
            for i in help_menu:
                markdown += ' - ' + i
            return markdown
    # async def on_message_activity(self):
    #     """
    #     I need to add the dialogue handling here - before anything else
    #     """
    #     # This will remove bot name if message was "at mention" to the bot
    #     if self.activity.get('roomType', '') == 'group':
    #         text = self.activity.get('text').replace(self.activity.get('bot_name') + ' ', '')
    #     else:
    #         text = self.activity.get('text', '')
    #
    #     # Begin check_campsites code
    #     if self.activity.get('dialogue_name') == 'check_campsites':
    #         if self.activity.get('dialogue_step') == 1:
    #             if not self.activity['inputs'].get('campground'):
    #                 message = dict(text=f"Please select a campground",
    #                                roomId=self.activity['roomId'],
    #                                attachments=[])
    #                 response = await self.webex_client.post_message_to_webex(message)
    #                 return response
    #             if not self.validate_date(self.activity['inputs']['start_date']):
    #                 message = dict(text=f"Start date {self.activity['inputs']['start_date']} is not valid",
    #                                roomId=self.activity['roomId'],
    #                                attachments=[])
    #                 response = await self.webex_client.post_message_to_webex(message)
    #                 return response
    #             if not self.validate_date(self.activity['inputs']['start_date']):
    #                 message = dict(text=f"End date {self.activity['inputs']['end_date']} is not valid",
    #                                roomId=self.activity['roomId'],
    #                                attachments=[])
    #                 response = await self.webex_client.post_message_to_webex(message)
    #                 return response
    #             if not self.validate_date_order(self.activity['inputs']['start_date'], self.activity['inputs']['end_date']):
    #                 message = dict(text=f"Start date {self.activity['inputs']['start_date']} is not before {self.activity['inputs']['end_date']}",
    #                                roomId=self.activity['roomId'],
    #                                attachments=[])
    #                 response = await self.webex_client.post_message_to_webex(message)
    #                 return response
    #
    #             cmd = f"nohup python3.7 {self.activity['inputs']['campground']} {self.activity['inputs']['start_date']} {self.activity['inputs']['end_date']} {self.activity['sender_email']} &"
    #             subprocess.call(cmd, shell=True)
    #
    #             # delete the record
    #             with pymongo.MongoClient(mongo_url) as client:
    #                 db = client[CONFIG.MONGO_DB_ACTIVITY]
    #                 posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
    #                 query_lab_filter = {'sender': self.activity.get('sender'),
    #                                     'roomId': self.activity.get('roomId'),
    #                                     'dialogue_name': 'check_campsites'}
    #                 try:
    #                     r = posts.delete_one(query_lab_filter)
    #                 except Exception as e:
    #                     print('Failed to connect to DB')
    #         message = dict(text='Search successfully created!',
    #                        roomId=self.activity['roomId'],
    #                        attachments=[])
    #         response = await self.webex_client.post_message_to_webex(message)
    #         return response
    #         # # if self.activity.get('dialogue_step') == 2:
    #
    #     # Begin delete_search code
    #     elif self.activity.get('dialogue_name') == 'delete_search':
    #         if self.activity.get('dialogue_step') == 1:
    #             print(self.activity)
    #             # 'campground': 'Disney', 'start_date': '01/04/2021', 'end_date': '01/05/2021'}
    #             print(self.activity.get('text'))
    #             if text in self.activity.get('valid_pids'):
    #                 cmd = f"kill {text}"
    #                 subprocess.call(cmd, shell=True)
    #                 with pymongo.MongoClient(mongo_url) as client:
    #                     db = client[CONFIG.MONGO_DB_ACTIVITY]
    #                     posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
    #                     query_lab_filter = {'sender': self.activity['sender'],
    #                                         'roomId': self.activity['roomId'],
    #                                         'dialogue_name': 'delete_search'}
    #                     try:
    #                         r = posts.delete_one(query_lab_filter)
    #                     except Exception as e:
    #                         print('Failed to connect to DB')
    #                 message = dict(text='Search successfully deleted!',
    #                                roomId=self.activity['roomId'],
    #                                attachments=[])
    #                 response = await self.webex_client.post_message_to_webex(message)
    #                 return response
    #             else:
    #                 message = dict(text=f"{text} if not a valid search.\nPlease Enter the PID of the search you would like to remove: ",
    #                                roomId=self.activity['roomId'],
    #                                attachments=[])
    #                 response = await self.webex_client.post_message_to_webex(message)
    #                 return response
    #
    #     # SHOULD BE A DIALOGUE
    #     elif text == 'check campsites' and not self.activity.get('dialogue_name'):
    #         # step 1 Creating check_campsites dialogue
    #         card_file = '/Users/stmosher/PycharmProjects/native_bot.py/cards/check_campsite.json'
    #         with open(f'{card_file}') as fp:
    #             text = fp.read()
    #         card = json.loads(text)
    #         message = dict(text=text,
    #                        roomId=self.activity['roomId'],
    #                        attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
    #         with pymongo.MongoClient(mongo_url) as client:
    #             db = client[CONFIG.MONGO_DB_ACTIVITY]
    #             posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
    #             query_lab_filter = {'sender': self.activity['sender'],
    #                                 'sender_email': self.activity['sender_email'],
    #                                 'roomId': self.activity['roomId'],
    #                                 'roomType': self.activity['roomType'],
    #                                 'id': self.activity['id'],
    #                                 'created': self.activity['created'],
    #                                 'dialogue_name': 'check_campsites',
    #                                 'dialogue_step': 1,
    #                                 'dialogue_max_steps': 2,
    #                                 'dialogue_data': []}
    #             try:
    #                 post_id = posts.insert_one(query_lab_filter).inserted_id
    #             except Exception as e:
    #                 print('Failed to connect to DB')
    #
    #         response = await self.webex_client.post_message_to_webex(message)
    #         return response
    #
    #     elif text.lower() == 'list searches':
    #         # results = [{search_id: pid, username: uid}]
    #         results = list()
    #         cmd = "ps -ef"
    #         args = shlex.split(cmd)
    #         proc = Popen(args, stdout=PIPE, stderr=PIPE)
    #         out, err = proc.communicate()
    #         exitcode = proc.returncode
    #         result = out.decode()
    #         result = result.split('\n')
    #         search_list = [x for x in result if 'check_disney.py' in x]
    #         print(search_list)
    #         for x in search_list:
    #             y = x.split()
    #             results.append(dict(campsite=y[8], process_id=y[1], start_date=y[9], end_date=y[10], sender_email=y[11]))
    #         print(results)
    #         message_text = 'Below are the current searches for Disney Campsites: \n'
    #         if not results:
    #             message_text += " - There are no active searches"
    #         else:
    #             for m in results:
    #                 message_text += f" - PID = {m['process_id']} Campsite: {m['campsite']} User: {m['sender_email']}  Start Date: {m['start_date']} End Date: {m['end_date']} \n"
    #         message = dict(text=message_text,
    #                        roomId=self.activity['roomId'],
    #                        attachments=[])
    #         response = await self.webex_client.post_message_to_webex(message)
    #         return response
    #     # Delete search code
    #     elif text.lower() == 'delete search':
    #         # step 1 Creating delete_search dialogue
    #         results = list()
    #         cmd = "ps -ef"
    #         args = shlex.split(cmd)
    #         proc = Popen(args, stdout=PIPE, stderr=PIPE)
    #         out, err = proc.communicate()
    #         exitcode = proc.returncode
    #         result = out.decode()
    #         result = result.split('\n')
    #         search_list = [x for x in result if 'check_disney.py' in x]
    #         for x in search_list:
    #             y = x.split()
    #             results.append(dict(campsite=y[8], process_id=y[1], start_date=y[9], end_date=y[10], sender_email=y[11]))
    #         if results:
    #             message_text = 'Below are the current searches for Disney Campsites: \n'
    #             valid_pids = list()
    #             for m in results:
    #                 valid_pids.append(m['process_id'])
    #                 message_text += f" - PID = {m['process_id']} Search: {m['campsite']} User: {m['sender_email']} Start Date: {m['start_date']} End Date: {m['end_date']} \n"
    #             message = dict(text=message_text,
    #                            roomId=self.activity['roomId'],
    #                            attachments=[])
    #             response = await self.webex_client.post_message_to_webex(message)
    #             message = dict(text="Please Enter the PID of the search you would like to remove: ",
    #                            roomId=self.activity['roomId'],
    #                            attachments=[])
    #             response = await self.webex_client.post_message_to_webex(message)
    #             with pymongo.MongoClient(mongo_url) as client:
    #                 db = client[CONFIG.MONGO_DB_ACTIVITY]
    #                 posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
    #                 query_lab_filter = {'sender': self.activity.get('sender', ''),
    #                                     'sender_email': self.activity.get('sender_email', ''),
    #                                     'roomId': self.activity.get('roomId', ''),
    #                                     'roomType': self.activity.get('roomType', ''),
    #                                     'id': self.activity.get('id', ''),
    #                                     'created': self.activity.get('created', ''),
    #                                     'dialogue_name': 'delete_search',
    #                                     'dialogue_step': 1,
    #                                     'dialogue_max_steps': 2,
    #                                     'dialogue_data': [],
    #                                     'valid_pids': valid_pids}
    #                 try:
    #                     post_id = posts.insert_one(query_lab_filter).inserted_id
    #                 except Exception as e:
    #                     print('Failed to connect to DB')
    #             return response
    #         else:
    #             message = dict(text='There are no active searches',
    #                            roomId=self.activity['roomId'],
    #                            attachments=[])
    #             response = await self.webex_client.post_message_to_webex(message)
    #             return response
    #