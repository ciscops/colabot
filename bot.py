#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import hashlib
import hmac
import json
import time
import logging
import aiohttp
import pymongo
import urllib3
from aiohttp.web_request import Request
from features.CML_chat import cml_chat
from features.small_talk import small_talk
from features import admin_actions
from features import awx
from features.catch_all import catch_all
from webex import WebExClient
from config import DefaultConfig as CONFIG


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

mongo_url = 'mongodb://' + CONFIG.MONGO_INITDB_ROOT_USERNAME + ':' + CONFIG.MONGO_INITDB_ROOT_PASSWORD + '@' + CONFIG.MONGO_SERVER + ':' + CONFIG.MONGO_PORT

help_menu_list = ['**CML delete lab** > delete lab\n',
                  '**CML list all labs** > list all labs\n',
                  '**CML list my lab details** > list your labs with details\n',
                  '**CML list my labs** > list only your labs\n',
                  '**CML list users** > list users\n',
                  '**CML show IP addresses** > show IP addresses\n',
                  '**CML show server utilization** > show current CPU and Memory usage\n',
                  '**CML stop lab** > stop labs of your choice\n',
                  '**Create AWS account** > create AWS COLAB account\n',
                  '**Create VPN account** > create an AnyConnect to COLAB VPN account\n',
                  '**Create accounts** > create base COLAB accounts\n',
                  '**Delete accounts** > delete COLAB accounts\n',
                  '**Reset passwords** > resets all COLAB associated passwords\n',
                  '**Admin alert CML users** > admins can alerts users of servers\n',
                  '**help** > display available commands\n']


class COLABot:

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
            logging.warning("Required: You must include a clientSigningSecret to verify incoming API webhooks")
            return {'status_code': 403}

        body = await req.read()
        logging.info('This is the initial message')
        key_bytes = self.webex_client_signing_secret.encode()
        hashed = hmac.new(key_bytes, body, hashlib.sha1)
        body_signature = hashed.hexdigest()
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
        logging.info('This is pre-db and NLP activity')
        logging.info(self.activity)
        if not self.activity:
            logging.error('Error - no activity')
            return {'status_code': 400}

        # Apply any security checks for incoming messages, i.e., domain name, room name, etc...
        if (self.activity.get('sender')) and (self.activity.get('sender') != CONFIG.BOT_ID) \
                and (self.activity.get('resource') == 'messages') and (self.activity.get('event') == 'created'):
            if CONFIG.AUTHORIZED_ROOMS:
                room_list = CONFIG.AUTHORIZED_ROOMS.split(',')
                denied = True
                for r in room_list:
                    response = await self.webex_client.get_room_memberships(r, self.activity['sender'])
                    if response.get('items'):
                        denied = False
                        break
                if denied:
                    logging.warning('Denied Access - user: %s', self.activity['sender'])
                    return {'status_code': 401}

        # Preprocess text
        if self.activity['description'] == 'message_details':
            if self.activity.get('roomType', '') == 'group':  # Remove bot name from text if message was "at mention"
                self.activity['text'] = self.activity.get('text').replace(self.activity.get('bot_name') + ' ', '')
        if self.activity.get('text'):
            self.activity['original_text'] = self.activity.get('text')
            self.activity['text'] = await self.preprocess(self.activity.get('text'))

        # Check activity for active dialogue. If active, apply saved dialogue data to activity
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            query_lab_filter = {'sender': self.activity.get('sender'),
                                'roomId': self.activity.get('roomId')}
            try:
                result = posts.find_one(query_lab_filter)  # Q: Is this lab already in DB?
            except Exception as e:
                logging.error('Failed to connect to DB')
                logging.error(e)
                return {'status_code': 500}

            # Check if dialogue record is too old, delete it
            pattern = '%Y-%m-%dT%H:%M:%S.%fZ'
            if result:
                epoch_time_now = time.time()
                last_dialogue_epoch_time = int(time.mktime(time.strptime(result['created'], pattern)))
                # If somehow the dialogue_max_step is maxed out
                if epoch_time_now - last_dialogue_epoch_time >= int(CONFIG.DIALOGUE_TIMEOUT) or result['dialogue_step'] > result['dialogue_max_steps']:  # Remove stale convos
                    try:
                        posts.delete_many(query_lab_filter)
                    except Exception as e:
                        logging.error('Could not remove stale dialogue record from DB')
                        logging.error(e)
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
                    self.activity['cml_password'] = result.get('cml_password', '')

        logging.info('This is the fully populated activity')
        logging.info(self.activity)

        if self.activity['description'] == 'bot_added':
            await self.bot_added()
        elif (self.activity['description'] == 'member_joined') and (self.activity['roomId'] == CONFIG.AUTHORIZED_ROOMS):
            message = dict(text=self.generate_welcome_message(),
                           roomId=self.activity['roomId'],
                           attachments=[])
            await self.webex_client.post_message_to_webex(message)
            await awx.create_accounts(self.activity)
        elif (self.activity['description'] == 'member_left') and (self.activity['roomId'] == CONFIG.AUTHORIZED_ROOMS):
            await awx.bot_delete_accounts(self.activity)
# Start Add elif for new Feature ---->
        # pointers to running dialogues
        elif self.activity.get('dialogue_name') == 'cml_alert_server_choices':
            await admin_actions.admin_alert_cml_users(self.activity)

        elif self.activity['description'] == 'card_details':
            if self.activity['inputs']['card_feature_index'] == 'cml':
                await cml_chat(self.activity)
            if self.activity['inputs']['card_feature_index'] == 'cml_alert':
                await admin_actions.admin_alert_cml_users(self.activity)
            if self.activity['inputs']['card_feature_index'] == 'colab':
                await awx.delete_accounts(self.activity)
            # Add new card activities here

        elif self.activity['description'] == 'message_details':

            # Webhook to NLP microservice
            try:
                result_nlp = await process_text(self.activity.get('text'))
                logging.info('NLP results')
                logging.info(result_nlp)
                if result_nlp[0][1] - result_nlp[1][1] > 0.12:  # TODO - need better solution here
                    self.activity['text'] = result_nlp[0][0]
                # Future - Can add a dialogue to ask user if highest confidence score was what they wanted
            except Exception as e:
                logging.warning('Unable to receive message from NLP server')
                logging.warning(e)

            logging.info('Below is the post NLP activity')
            logging.info(self.activity)

            # Main Message Activities
            if self.activity.get('text') == 'help':
                await self.display_help_menu()

            elif self.activity.get('text') == 'create accounts' or self.activity.get('text') == 'reset passwords':
                await awx.create_accounts(self.activity)

            elif self.activity.get('text') == 'create aws account':
                await awx.create_aws_account(self.activity)

            elif self.activity.get('text') == 'create vpn account':
                await awx.create_vpn_account(self.activity)

            elif self.activity.get('text') == 'delete accounts':
                await awx.delete_accounts(self.activity)

            elif self.activity.get('text')[:3] == 'cml':  # Add searches for cml dialogue here
                logging.debug('matched cml')
                await cml_chat(self.activity)

            elif self.activity.get('text')[:3] == 'bye':
                await small_talk(self.activity)

            elif self.activity.get('text')[:6] == 'thanks':
                await small_talk(self.activity)

            elif self.activity.get('text')[:12] == 'troubleshoot':
                await small_talk(self.activity)

            elif self.activity.get('text') == 'upset':
                await small_talk(self.activity)

            elif self.activity.get('text') == 'accept_apology':
                await small_talk(self.activity)

            elif self.activity.get('text') == 'affirmation':
                await small_talk(self.activity)

            elif self.activity.get('text') == 'admin alert cml users':
                await admin_actions.admin_alert_cml_users(self.activity)

            # Add new text message activities here
# End Add elif for new Feature ---->

            else:
                if self.activity.get('description') == 'card_details':
                    await self.card_catch_all()
                else:
                    await catch_all(self.activity)
        return {'status_code': 200}

    async def display_help_menu(self):
        message = dict(text=self.generate_help_menu_markdown(help_menu_list),
                       roomId=self.activity['roomId'],
                       attachments=[])
        response = await self.webex_client.post_message_to_webex(message)
        return response

    async def card_catch_all(self):
        if self.activity.get('description') == 'card_details':
            message = dict(text='The card is inactive. Please generate a new one.',
                           roomId=self.activity['roomId'],
                           attachments=[])
            await self.webex_client.post_message_to_webex(message)

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

        elif request_dict['resource'] == 'memberships' and request_dict['event'] == 'created' and request_dict['data'][
                'personId'] != CONFIG.BOT_ID:
            activity = {'id': request_dict['data']['id'],
                        'resource': request_dict['resource'],
                        'event': request_dict['event'],
                        'sender': request_dict['data']['personId'],
                        'sender_email': request_dict['data']['personEmail'],
                        'person_display_name': request_dict['data']['personDisplayName'],
                        'roomId': request_dict['data']['roomId'],
                        'created': request_dict['data']['created'],
                        'roomType': request_dict['data']['roomType'],
                        'description': 'member_joined',
                        'bot_name': CONFIG.BOT_NAME,
                        'webex_bot_token': self.webex_bot_token}

        elif request_dict['resource'] == 'memberships' and request_dict['event'] == 'deleted' and request_dict['data'][
                'personId'] != CONFIG.BOT_ID:
            activity = {'id': request_dict['data']['id'],
                        'resource': request_dict['resource'],
                        'event': request_dict['event'],
                        'sender': request_dict['data']['personId'],
                        'sender_email': request_dict['data']['personEmail'],
                        'person_display_name': request_dict['data']['personDisplayName'],
                        'roomId': request_dict['data']['roomId'],
                        'created': request_dict['data']['created'],
                        'roomType': request_dict['data']['roomType'],
                        'description': 'member_left',
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
                        'parentId': message_body.get('parentId', ''),
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
        if (self.activity['roomType'] == 'group') and (self.activity['roomId'] == CONFIG.AUTHORIZED_ROOMS):
            markdown = 'Hi, See my available commands below: \n'
            for i in help_menu:
                markdown += ' - ' + '**' + '@' + self.activity['bot_name'] + '** ' + i
        elif (self.activity['roomType'] == 'group') and (self.activity['roomId'] != CONFIG.AUTHORIZED_ROOMS):
            markdown = 'Hi, You must also be a member of the "CoLAB Users" space for me to respond. Below are my available commands: \n'
            for i in help_menu:
                markdown += ' - ' + '**' + '@' + self.activity['bot_name'] + '** ' + i
        else:
            markdown = 'Hi, See my available commands below: \n'
            for i in help_menu:
                markdown += ' - ' + i
        markdown += '\nor visit https://confluence-eng-rtp1.cisco.com/conf/display/CIDR/CoLaboratory for more information.\n'
        return markdown

    def generate_welcome_message(self):
        if self.activity['roomType'] == 'group':
            markdown = f"Welcome <@personEmail:{self.activity.get('sender_email')}|{self.activity.get('person_display_name')}>! \n\nI'm the CoLaboratory admin bot. I'm creating your base COLAB accounts. By using the Colaboratory resources you are agreeing to the Rules of the Road which can be found at \nhttps://confluence-eng-rtp1.cisco.com/conf/display/CIDR/Colaboratory+Rules+of+the+Road. \n\nI will direct message your new credentials shortly. "
            markdown += "Please message " + '**' + '@' + self.activity['bot_name'] + '** ' + "**help** to see my available commands."
        else:
            markdown = f"Welcome <@personEmail:{self.activity.get('sender_email')}|{self.activity.get('person_display_name')}>! \n\nI'm the CoLaboratory admin bot. I'm creating your base COLAB accounts. By using the Colaboratory resources you are agreeing to the Rules of the Road which can be found \nhttps://confluence-eng-rtp1.cisco.com/conf/display/CIDR/Colaboratory+Rules+of+the+Road. \n\nI will direct message your new credentials shortly. Please message **help** to see my available commands."
        return markdown

    @staticmethod
    async def preprocess(text):
        text = [word.lower().strip() for word in text.split()]
        text = [''.join(c for c in s if c not in string.punctuation) for s in text]
        return [' '.join(x for x in text if x)][0]


async def process_text(message):
    api_path = '/api/v1/nlp'
    headers = {
        'Content-Type': 'application/json'
    }
    body = {'text': message, 'secret': CONFIG.NLP_SECRET}
    u = 'http://' + CONFIG.NLP_SERVER + api_path
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
    try:
        async with session.request(method="POST", url=u, headers=headers, data=json.dumps(body), ssl=False) as res:
            response_content = {}
            response_content = await res.json()
            await session.close()
            return response_content.get('scores')
    except Exception as e:
        logging.warning('warning from process_text')
        logging.warning(e)
        try:
            await session.close()
        except Exception as e1:
            logging.warning(e1)
        return response_content
