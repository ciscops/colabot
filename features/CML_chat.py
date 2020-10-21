from .CML import CML
from config import DefaultConfig as CONFIG
from features.catch_all import catch_all
from webex import WebExClient
import json
import pymongo
from jinja2 import Template
import time
import re
import copy
import logging


mongo_url = 'mongodb://' + CONFIG.MONGO_INITDB_ROOT_USERNAME + ':' + CONFIG.MONGO_INITDB_ROOT_PASSWORD + '@' + CONFIG.MONGO_SERVER + ':' + CONFIG.MONGO_PORT


async def cml_chat(activity):
    cml_servers = CONFIG.SERVER_LIST.split(',')

    """START CML LIST ALL LABS"""
    if activity.get('text') == 'cml list all labs':
        logging.debug('in cml list all labs')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for cml_server in cml_servers:
            results_message = ''
            logging.debug(cml_server)
            on_server = False
            server_name = '\n***' + cml_server + '***\n'
            cml = CML(CONFIG.CML_USERNAME, CONFIG.CML_PASSWORD, cml_server)
            # Get bearer token
            if not await cml.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ***' + cml_server + '***: ' + str(
                    cml.status_code) + ' ' + str(cml.bearer_token),
                               roomId=activity['roomId'],
                               parentId=activity['parentId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue

            if not await cml.get_diagnostics():
                message = dict(text='Error retrieving diagnostics ***' + cml_server + '***: ' + str(cml.diagnostics),
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            epoch_time_now = int(time.time())

            for k, v in cml.diagnostics['user_roles']['labs_by_user'].items():
                logging.debug(k)
                logging.debug(v)
                labs_flag = False
                lab_string = '\nLabs for account: ***' + k + '***\n\n'
                logging.debug('begin: ' + lab_string)
                # lab_string = ''
                for i in v:
                    logging.debug('This is i: ')
                    logging.debug(i)
                    labs_flag = True
                    created_seconds = cml.diagnostics['labs'][i]['created']
                    delta = epoch_time_now - created_seconds
                    days = int(delta // 86400)
                    hours = int(delta // 3600 % 24)
                    minutes = int(delta // 60 % 60)
                    seconds = int(delta % 60)
                    uptime = str(days) + ' Days, ' + str(hours) + ' Hrs, ' + str(minutes) + ' Mins, ' + str(
                        seconds) + ' Secs'
                    logging.debug(uptime)
                    lab_string += ' -  Lab Id: ' + i + ' Uptime: ' + uptime + '\n'
                logging.debug('end: ' + lab_string)
                if labs_flag:
                    on_server = True
                    server_name += lab_string
            if on_server:
                results_message += server_name
            logging.debug('This is the message: ')
            logging.debug(results_message)
            logging.debug(activity['roomId'])
            message = dict(text=results_message,
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
        return
    """END CML LIST ALL LABS"""

    """START CML LIST USERS"""
    if activity.get('text') == 'cml list users':
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for cml_server in cml_servers:
            results_message = ''
            server_name = '\n***' + cml_server + '***\n'
            cml = CML(CONFIG.CML_USERNAME, CONFIG.CML_PASSWORD, cml_server)
            # Get bearer token
            if not await cml.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + cml_server + ': ' + str(
                    cml.status_code) + ' ' + str(cml.bearer_token),
                               roomId=activity['roomId'],
                               parentId=activity['parentId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue

            if not await cml.get_users():
                server_name += 'Error accessing server ' + cml_server + ': ' + str(
                    cml.status_code) + ' ' + cml.users.get('description', '')
            else:
                for key in cml.users:
                    server_name += ' - ' + key + '\n'
            results_message += server_name

            message = dict(text=results_message,
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
        return
    """END CML LIST USERS"""

    """START CML LIST MY LABS"""
    if activity.get('text') == 'cml list my labs':
        results_message = ''
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        epoch_time_now = int(time.time())
        for cml_server in cml_servers:
            labs_flag = False
            server_name = '\n***' + cml_server + '***\n'
            cml = CML(CONFIG.CML_USERNAME, CONFIG.CML_PASSWORD, cml_server)
            # Get bearer token
            if not await cml.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + cml_server + ': ' + str(
                    cml.status_code) + ' ' + str(cml.bearer_token),
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue

            if not await cml.get_diagnostics():
                server_name += 'Error accessing server ' + cml_server + ': ' + str(
                    cml.status_code) + ' ' + cml.diagnostics.get('description', '')
            else:
                labs = cml.diagnostics['user_roles']['labs_by_user'].get(user_and_domain[0], [])
                for lab in labs:
                    created_seconds = cml.diagnostics['labs'][lab]['created']
                    labs_flag = True
                    delta = epoch_time_now - created_seconds
                    days = int(delta // 86400)
                    hours = int(delta // 3600 % 24)
                    minutes = int(delta // 60 % 60)
                    seconds = int(delta % 60)
                    uptime = str(days) + ' Days, ' + str(hours) + ' Hrs, ' + str(minutes) + ' Mins, ' + str(
                        seconds) + ' Secs'

                    server_name += ' -  Lab Id: ' + lab + ' Uptime: ' + uptime + '\n'
            if labs_flag:
                results_message += server_name
        if results_message:
            message = dict(text=results_message,
                           roomId=activity['roomId'],
                           attachments=[])
        else:
            message = dict(text="You don't have any labs",
                           roomId=activity['roomId'],
                           attachments=[])
        await webex.post_message_to_webex(message)
        return
    """END CML LIST MY LABS"""

    """START CML SHOW SERVER UTILIZATION"""
    if activity.get('text') == 'cml show server utilization':
        results_message = ''
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for cml_server in cml_servers:
            server_name = '\n***' + cml_server + '***\n'
            cml = CML(CONFIG.CML_USERNAME, CONFIG.CML_PASSWORD, cml_server)
            # Get bearer token
            if not await cml.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + cml_server + ': ' + str(
                    cml.status_code) + ' ' + str(cml.bearer_token),
                               roomId=activity['roomId'],
                               parentId=activity['parentId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue

            if not await cml.get_system_status():
                server_name += 'Error accessing server ' + cml_server + ': ' + str(
                    cml.status_code) + ' ' + cml.system_status.get('description', '')
            else:
                cpu = round(
                    cml.system_status['clusters']['cluster_1']['high_level_drivers']['compute_1']['cpu']['percent'])
                memory = round(
                    cml.system_status['clusters']['cluster_1']['high_level_drivers']['compute_1']['memory']['used'] /
                    cml.system_status['clusters']['cluster_1']['high_level_drivers']['compute_1']['memory'][
                        'total'] * 100)

                server_name += ' -  CPU: ' + str(cpu) + '% Memory: ' + str(memory) + '%\n'
                results_message += server_name
        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return
    """END CML SHOW SERVER UTILIZATION"""

    """START CML EXTEND LAB"""

    if re.search('^CML extend lab .*', activity.get('text', '')):
        temp = activity.get('text').split('lab')
        lab = temp[1].strip()
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB]
            posts = db[CONFIG.MONGO_COLLECTIONS]
            query_lab_filter = {'user_id': activity.get('sender', ''),
                                'lab_id': lab}
            result = posts.find(query_lab_filter)
            epoch_time_now = int(time.time())
            doc = posts.find_one_and_update(query_lab_filter,
                                            {'$set': {'warning_date': epoch_time_now, 'renewal_flag': True}})

        if not doc:
            results_message = 'Not able to find lab: ' + lab
        else:
            results_message = lab + ' Successfully extended'

        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return
    """END CML EXTEND LAB"""

    """START CML STOP LAB DIALOGUE"""
    if activity.get('text') == 'cml stop lab':
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        card_file = './cards/cml_stop_lab_get_password.json'
        with open(f'{card_file}') as fp:
            text = fp.read()
        card = json.loads(text)

        # If group then send a DM with a card
        if activity.get('roomType', '') == 'group':
            message = dict(text='Stop CML lab',
                           toPersonId=activity['sender'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            result = await webex.post_message_to_webex(message)

            message = dict(text="I've direct messaged you. Let's continue this stop lab request in private.",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            activity['roomId'] = result.get('roomId', '')
        # if direct, send a card to the same room
        else:
            message = dict(text='Stop CML lab',
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
                               'dialogue_name': 'cml_stop_lab',
                               'dialogue_step': 1,
                               'dialogue_max_steps': 2,
                               'dialogue_data': [],
                               'card_dialogue_index': 'cml_stop_lab',
                               'card_feature_index': 'cml'}
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
            except Exception as e:
                print('Failed to connect to DB')
        return
    if activity.get('dialogue_name') == 'cml_stop_lab' and activity.get('dialogue_step') == 1:
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        running_labs_for_card = ''
        for cml_server in cml_servers:
            try:
                cml_user = CML(user_and_domain[0], activity['inputs']['cml_password'], cml_server)
            except:
                message = dict(text='I thought we were talking about stopping a lab. Please send a new command',
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                # Remove dialogue from DB
                with pymongo.MongoClient(mongo_url) as client:
                    db = client[CONFIG.MONGO_DB_ACTIVITY]
                    posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                    query_lab_filter = {'sender': activity['sender'],
                                        'roomId': activity['roomId'],
                                        'dialogue_name': 'cml_stop_lab'}
                return
            # Get bearer token
            if not await cml_user.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + cml_server + ': ' + str(
                    cml_user.status_code) + ' ' + cml_user.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            # list the current users labs
            if not await cml_user.get_user_labs():
                message = dict(text='Error accessing server ' + cml_server + ': ' + str(
                    cml_user.status_code) + ' ' + cml_user.user_labs.get('description', ''),
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            lab_details = list()
            for lab in cml_user.user_labs:
                if await cml_user.get_user_lab_details(lab):
                    lab_details.append(cml_user.user_lab_details)
            final = ''
            running_labs = False
            if lab_details:
                lab_choices_string = '{"type": "TextBlock","text": "' + cml_server + '"},' + '{"type": "Input.ChoiceSet","id": "' + cml_server + '","style": "expanded","value": "1","choices": ['
                for i in lab_details:
                    if i['state'] == 'STARTED':
                        running_labs = True
                        temp_string = i['lab_title'] + '   Created: ' + i['created']
                        temp_details = i['id']
                        lab_choices_string += '{"title": "' + temp_string + '","value": "' + temp_details + '"},'
                    final = lab_choices_string[:-1]
                    final += '],"isMultiSelect": true},'
                if running_labs:
                    running_labs_for_card += final
        if running_labs_for_card:
            with open('cards/cml_stop_lab_choices.json') as file_:
                template = Template(file_.read())
            card = template.render(lab_choices=running_labs_for_card)
            card_json = json.loads(card)
            message = dict(text='Stop CML lab',
                           roomId=activity['roomId'],
                           attachments=[
                               {'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card_json}])
            result = await webex.post_message_to_webex(message)

            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                try:
                    doc = posts.find_one_and_update(
                        {'id': activity['id']},
                        {'$set': {'dialogue_step': 2,
                                  'card_dialogue_index': 'cml_stop_lab_choices',
                                  'cml_password': activity['inputs']['cml_password']}
                         }
                    )
                except Exception as e:
                    print('Failed to connect to DB')
            return
        else:
            message = dict(text="You don't have running labs",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            # Delete the dialogue record
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                query_lab_filter = {'sender': activity['sender'],
                                    'roomId': activity['roomId'],
                                    'dialogue_name': 'cml_stop_lab'}
                try:
                    r = posts.delete_one(query_lab_filter)
                except Exception as e:
                    print('Failed to connect to DB')

            return
    if activity.get('card_dialogue_index') == 'cml_stop_lab_choices' and activity.get('dialogue_step') == 2:
        results_message = ''
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for cml_server in cml_servers:
            if activity['inputs'].get(cml_server):
                cml_user = CML(user_and_domain[0], activity['cml_password'], cml_server)
                # If the user is not there, the below won't work
                if not await cml_user.get_token():
                    message = dict(
                        text='Error accessing server ' + cml_server + ': ' + str(
                            cml_user.status_code) + ' ' + cml_user.bearer_token,
                        roomId=activity['roomId'],
                        attachments=[])
                    await webex.post_message_to_webex(message)
                    continue
                labs_list = activity['inputs'].get(cml_server).split(',')
                for lab in labs_list:
                    if not await cml_user.stop_lab(lab):
                        print('stop lab')
                        print(str(cml_user.status_code))
                        print(cml_user.result.get('description', ''))
                        results_message += ' - ' + cml_server + ' Fail: ' + str(
                            cml_user.status_code) + ' ' + cml_user.result.get('description', '') + '\n'
                    else:
                        results_message += ' - ' + cml_server + ' Lab Id: ' + lab + ' Stopped!' + '\n'

        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        # Remove dialogue from DB
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            query_lab_filter = {'sender': activity['sender'],
                                'roomId': activity['roomId'],
                                'dialogue_name': 'cml_stop_lab'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                print('Failed to connect to DB')

        return
    """ END CML STOP LAB DIALOGUE """

    """START CML DELETE LAB DIALOGUE"""
    if activity.get('text') == 'cml delete lab':
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        card_file = './cards/cml_delete_lab_get_password.json'
        with open(f'{card_file}') as fp:
            text = fp.read()
        card = json.loads(text)

        # If group then send a DM with a card
        if activity.get('roomType', '') == 'group':
            message = dict(text='Stop CML lab',
                           toPersonId=activity['sender'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            result = await webex.post_message_to_webex(message)
            message = dict(text="I've direct messaged you. Let's continue this stop lab request in private.",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            activity['roomId'] = result.get('roomId', '')
        # if direct, send a card to the same room
        else:
            message = dict(text='Delete CML lab',
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
                               'dialogue_name': 'cml_delete_lab',
                               'dialogue_step': 1,
                               'dialogue_max_steps': 2,
                               'dialogue_data': [],
                               'card_dialogue_index': 'cml_delete_lab',
                               'card_feature_index': 'cml'}
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
            except Exception as e:
                print('Failed to connect to DB')
        return
    if activity.get('dialogue_name') == 'cml_delete_lab' and activity.get('dialogue_step') == 1:
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        labs_for_card = ''
        for cml_server in cml_servers:
            try:
                cml_user = CML(user_and_domain[0], activity['inputs']['cml_password'], cml_server)
            except:
                message = dict(text='I thought we were talking about deleting a lab. Please send a new command',
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                # Remove dialogue from DB
                with pymongo.MongoClient(mongo_url) as client:
                    db = client[CONFIG.MONGO_DB_ACTIVITY]
                    posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                    query_lab_filter = {'sender': activity['sender'],
                                        'roomId': activity['roomId'],
                                        'dialogue_name': 'cml_delete_lab'}
                return

            # Get bearer token
            if not await cml_user.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + cml_server + ': ' + str(
                    cml_user.status_code) + ' ' + cml_user.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            # list the current users labs
            if not await cml_user.get_user_labs():
                message = dict(text='Error accessing server ' + cml_server + ': ' + str(
                    cml_user.status_code) + ' ' + cml_user.user_labs.get('description', ''),
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            lab_details = list()
            for lab in cml_user.user_labs:
                if await cml_user.get_user_lab_details(lab):
                    lab_details.append(cml_user.user_lab_details)
            final = ''
            if lab_details:
                lab_choices_string = '{"type": "TextBlock","text": "' + cml_server + '"},' + '{"type": "Input.ChoiceSet","id": "' + cml_server + '","style": "expanded","value": "1","choices": ['
                for i in lab_details:
                    temp_string = i['lab_title'] + '   Created: ' + i['created']
                    temp_details = i['id']
                    lab_choices_string += '{"title": "' + temp_string + '","value": "' + temp_details + '"},'
                    final = lab_choices_string[:-1]
                    final += '],"isMultiSelect": true},'

                labs_for_card += final
        if labs_for_card:
            with open('cards/cml_delete_lab_choices.json') as file_:
                template = Template(file_.read())
            card = template.render(lab_choices=labs_for_card)
            card_json = json.loads(card)
            message = dict(text='CML delete lab',
                           roomId=activity['roomId'],
                           attachments=[
                               {'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card_json}])
            result100 = await webex.post_message_to_webex(message)
            # This needs to be an update
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                try:
                    doc = posts.find_one_and_update(
                        {'id': activity['id']},
                        {'$set': {'dialogue_step': 2,
                                  'card_dialogue_index': 'cml_delete_lab_choices',
                                  'cml_password': activity['inputs']['cml_password']}
                         }
                    )
                except Exception as e:
                    print('Failed to connect to DB')
            return
        else:
            message = dict(text="You don't have labs",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            # Delete the dialogue record
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                query_lab_filter = {'sender': activity['sender'],
                                    'roomId': activity['roomId'],
                                    'dialogue_name': 'cml_delete_lab'}
                try:
                    r = posts.delete_one(query_lab_filter)
                except Exception as e:
                    print('Failed to connect to DB')

            return
    if activity.get('card_dialogue_index') == 'cml_delete_lab_choices' and activity.get('dialogue_step') == 2:
        results_message = ''
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for cml_server in cml_servers:
            if activity['inputs'].get(cml_server):
                cml_user = CML(user_and_domain[0], activity['cml_password'], cml_server)
                # If the user is not there, the below won't work
                if not await cml_user.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                    message = dict(
                        text='Error accessing server ' + cml_server + ': ' + str(
                            cml_user.status_code) + ' ' + cml_user.bearer_token,
                        roomId=activity['roomId'],
                        attachments=[])
                    await webex.post_message_to_webex(message)
                    continue
                labs_list = activity['inputs'].get(cml_server).split(',')
                for lab in labs_list:
                    if not await cml_user.stop_lab(lab):
                        print('stop lab')
                        print(str(cml_user.status_code))
                        print(cml_user.result.get('description', ''))
                    if not await cml_user.wipe_lab(lab):
                        print('wipe lab')
                        print(str(cml_user.status_code))
                        print(cml_user.result.get('description', ''))
                    if not await cml_user.delete_lab(lab):
                        print('delete lab')
                        print(str(cml_user.status_code))
                        print(cml_user.result.get('description', ''))
                        results_message += ' - ' + cml_server + ' Fail: ' + str(
                            cml_user.status_code) + ' ' + cml_user.result.get('description', '') + '\n'
                    else:
                        results_message += ' - ' + cml_server + ' Lab Id: ' + lab + ' Deleted!' + '\n'

        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        # Remove dialogue from DB
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            query_lab_filter = {'sender': activity['sender'],
                                'roomId': activity['roomId'],
                                'dialogue_name': 'cml_delete_lab'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                print('Failed to connect to DB')

        return
    """ END CML DELETE LAB DIALOGUE """

    """START CML LIST MY LAB DETAILS DIALOGUE"""
    if activity.get('text') == 'cml list my lab details':
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        card_file = './cards/list_my_lab_details_get_password.json'
        with open(f'{card_file}') as fp:
            text = fp.read()
        card = json.loads(text)

        # If group then send a DM with a card
        if activity.get('roomType', '') == 'group':
            message = dict(text='List my lab details',
                           toPersonId=activity['sender'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            result = await webex.post_message_to_webex(message)
            message = dict(text="I've direct messaged you. Let's continue this request in private.",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            activity['roomId'] = result.get('roomId', '')
        # if direct, send a card to the same room
        else:
            message = dict(text='List my lab details',
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
                               'dialogue_name': 'cml_list_lab_details',
                               'dialogue_step': 1,
                               'dialogue_max_steps': 2,
                               'dialogue_data': [],
                               'card_dialogue_index': 'cml_list_lab_details',
                               'card_feature_index': 'cml'}
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
            except Exception as e:
                print('Failed to connect to DB')
        return
    if activity.get('dialogue_name') == 'cml_list_lab_details' and activity.get('dialogue_step') == 1:
        results_message = ''
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for cml_server in cml_servers:
            try:
                cml_user = CML(user_and_domain[0], activity['inputs']['cml_password'], cml_server)
            except:
                message = dict(text='I thought we were talking about lab details. Please send a new command',
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                # Remove dialogue from DB
                with pymongo.MongoClient(mongo_url) as client:
                    db = client[CONFIG.MONGO_DB_ACTIVITY]
                    posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                    query_lab_filter = {'sender': activity['sender'],
                                        'roomId': activity['roomId'],
                                        'dialogue_name': 'cml_list_lab_details'}
                return
            # Get bearer token
            # If the user is not there, the below won't work
            if not await cml_user.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + cml_server + ': ' + str(
                    cml_user.status_code) + ' ' + cml_user.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            # list the current users labs
            if not await cml_user.get_user_labs():
                message = dict(text='Error accessing server ' + cml_server + ': ' + str(
                    cml_user.status_code) + ' ' + cml_user.user_labs.get('description', ''),
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            lab_details = list()
            for lab in cml_user.user_labs:
                if await cml_user.get_user_lab_details(lab):
                    lab_details.append(cml_user.user_lab_details)

            if lab_details:
                results_message += '\n' + cml_server + ' labs are: \n'
                for lab in lab_details:
                    results_message += ' - Lab Title: ' + lab['lab_title'] + ' Lab Id:: ' + lab['id'] + ' Created: ' + \
                                       lab['created'] + ' State: ' + lab['state'] + '\n'
        if results_message:
            message = dict(text=results_message,
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
        else:
            message = dict(text='You have no labs',
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
        # Delete the dialogue record
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            query_lab_filter = {'sender': activity['sender'],
                                'roomId': activity['roomId'],
                                'dialogue_name': 'cml_list_lab_details'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                print('Failed to connect to DB')

        return
    """END CML LIST MY LAB DETAILS DIALOGUE"""

    """START CML SHOW IPS DIALOGUE"""
    if activity.get('text') == 'cml show ip addresses':
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        card_file = './cards/cml_ips_get_password.json'
        with open(f'{card_file}') as fp:
            text = fp.read()
        card = json.loads(text)

        # If group then send a DM with a card
        if activity.get('roomType', '') == 'group':
            message = dict(text='Get IP addresses',
                           toPersonId=activity['sender'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            result = await webex.post_message_to_webex(message)
            message = dict(text="I've direct messaged you. Let's continue this request in private.",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            activity['roomId'] = result.get('roomId', '')
        # if direct, send a card to the same room
        else:
            message = dict(text='Get IP addresses',
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
                               'dialogue_name': 'cml_ips_lab',
                               'dialogue_step': 1,
                               'dialogue_max_steps': 2,
                               'dialogue_data': [],
                               'card_dialogue_index': 'cml_ips_lab',
                               'card_feature_index': 'cml'}
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
            except Exception as e:
                print('Failed to connect to DB')
        return
    if activity.get('dialogue_name') == 'cml_ips_lab' and activity.get('dialogue_step') == 1:
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for cml_server in cml_servers:
            message_text = f'{cml_server}\n'
            try:
                cml_user = CML(user_and_domain[0], activity['inputs']['cml_password'], cml_server)
            except:
                message = dict(text='I thought we were talking about getting your lab IP addresses. Please send a new command',
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                # Remove dialogue from DB
                with pymongo.MongoClient(mongo_url) as client:
                    db = client[CONFIG.MONGO_DB_ACTIVITY]
                    posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                    query_lab_filter = {'sender': activity['sender'],
                                        'roomId': activity['roomId'],
                                        'dialogue_name': 'cml_ips_lab'}
                return

            # Get bearer token
            if not await cml_user.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message_text += f" * Error accessing server {cml_server} : {str(cml_user.status_code)} {cml_user.bearer_token}\n"
                continue
            # list the current users labs
            if not await cml_user.get_user_labs():
                message_text += f" * Error accessing server {cml_server} : {str(cml_user.status_code)} {cml_user.user_labs.get('description', '')}\n"
                continue
            lab_address_results = list()  # [{'lab_id': '9eecab', 'nodes': [{'node_id': 'n0', 'node_name': 'csr1000v-0', 'interfaces': [{'interface_name': 'GigabitEthernet1', 'ip4': ['192.133.186.51']]}]}]
            for lab in cml_user.user_labs:
                temp_lab_dict = {'lab_id': lab, 'nodes': []}
                if await cml_user.get_lab_nodes(lab):
                    for node in cml_user.lab_nodes:
                        temp_node_dict = {'node_id': node, 'interfaces': []}
                        if await cml_user.layer3_addresses(lab, node):
                            temp_node_dict['node_name'] = cml_user.lab_int_addresses.get('name')
                            if cml_user.lab_int_addresses.get('interfaces'):
                                for k in cml_user.lab_int_addresses['interfaces'].keys():
                                    if cml_user.lab_int_addresses['interfaces'][k]['ip4']:
                                        temp_interface_dict = {'interface_name': cml_user.lab_int_addresses['interfaces'][k]['label']}
                                        temp_interface_dict['ip4'] = copy.deepcopy(cml_user.lab_int_addresses['interfaces'][k]['ip4'])
                                        temp_node_dict['interfaces'].append(temp_interface_dict)
                        if temp_node_dict['interfaces']:
                            temp_lab_dict['nodes'].append(temp_node_dict)
                if temp_lab_dict['nodes']:
                    lab_address_results.append(temp_lab_dict)
            if lab_address_results:
                for lab in lab_address_results:
                    if await cml_user.get_user_lab_details(lab['lab_id']):
                        lab['lab_title'] = cml_user.user_lab_details.get('lab_title')
                    else:
                        lab['lab_title'] = ''
                    message_text += f" * Lab title: {lab['lab_title']} Lab id: {lab['lab_id']}\n"
                    for node in lab['nodes']:
                        message_text += f"     - Node: {node['node_name']}\n"
                        for interface in node['interfaces']:
                            ips = ''
                            for ip in interface['ip4']:
                                ips += ' ' + ip
                            message_text += f"         - {interface.get('interface_name')}:{ips}\n"

            else:
                message_text += f" * None\n"

            message = dict(text=message_text,
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)

        # Remove dialogue from DB
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            query_lab_filter = {'sender': activity['sender'],
                                'roomId': activity['roomId'],
                                'dialogue_name': 'cml_ips_lab'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                print('Failed to connect to DB')

        return
    """ END CML SHOW IPS DIALOGUE """

    """START CATCH ALL"""
    await catch_all(activity)
    return
    """END CATCH ALL"""
