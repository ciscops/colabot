from .VIRL import VIRL
from config import DefaultConfig as CONFIG
from webex import WebExClient
import json
import pymongo
from jinja2 import Template
import time
import re


mongo_url = 'mongodb://' + CONFIG.MONGO_INITDB_ROOT_USERNAME + ':' + CONFIG.MONGO_INITDB_ROOT_PASSWORD + '@' + CONFIG.MONGO_SERVER + ':' + CONFIG.MONGO_PORT


async def virl_chat(activity):
    virl_servers = CONFIG.SERVER_LIST.split(',')

    """START VIRL CREATE ACCOUNT"""
    if activity.get('text') == 'VIRL create account':
        results_message = ''
        pwd = VIRL.password_generator()
        check_flag = False
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for virl_server in virl_servers:
            virl = VIRL(CONFIG.VIRL_USERNAME, CONFIG.VIRL_PASSWORD, virl_server)
            # Get bearer token
            if not await virl.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl.status_code) + ' ' + virl.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            user_and_domain = activity['sender_email'].split('@')
            if not await virl.add_user(username_webex=user_and_domain[0],
                                       user_email=activity['sender_email'],
                                       new_password=pwd):
                results_message += ' - ' + virl_server + ' Failed: ' + virl.result.get('description', '') + '\n'
            else:
                check_flag = True
                results_message += ' - ' + virl_server + ' Success! \n'

        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        if check_flag:
            message = dict(text='VIRL password: ' + pwd,
                           toPersonId=activity['sender'],
                           attachments=[])
            await webex.post_message_to_webex(message)
        return {'status_code': 200}
    """END  VIRL CREATE ACCOUNT"""

    """START VIRL RESET PASSWORD"""
    if activity.get('text') == 'VIRL reset password':
        results_message = ''
        pwd = VIRL.password_generator()
        check_flag = False
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for virl_server in virl_servers:
            virl = VIRL(CONFIG.VIRL_USERNAME, CONFIG.VIRL_PASSWORD, virl_server)
            # Get bearer token
            if not await virl.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl.status_code) + ' ' + virl.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            user_and_domain = activity['sender_email'].split('@')
            if not await virl.change_password(username_webex=user_and_domain[0],
                                              new_password=pwd):
                results_message += ' - ' + virl_server + ' Fail: ' + str(virl.status_code) + ' ' + virl.result.get('description', '') + '\n'
            else:
                check_flag = True
                results_message += ' - ' + virl_server + ' Success: ' + str(virl.status_code) + '\n'

        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        if check_flag:
            message = dict(text='VIRL password: ' + pwd,
                           toPersonId=activity['sender'],
                           attachments=[])
            await webex.post_message_to_webex(message)
        return {'status_code': 200}
    """END VIRL RESET PASSWORD"""

    """START VIRL LIST ALL LABS"""
    if activity.get('text') == 'VIRL list all labs':
        results_message = ''
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for virl_server in virl_servers:
            on_server = False
            server_name = '\n***' + virl_server + '***\n'
            virl = VIRL(CONFIG.VIRL_USERNAME, CONFIG.VIRL_PASSWORD, virl_server)
            # Get bearer token
            if not await virl.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl.status_code) + ' ' + virl.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue

            await virl.get_diagnostics()
            epoch_time_now = int(time.time())

            for k, v in virl.diagnostics['user_roles']['labs_by_user'].items():
                labs_flag = False
                lab_string = '\nLabs for account: ***' + k + '***\n\n'
                # lab_string = ''
                for i in v:
                    labs_flag = True
                    created_seconds = virl.diagnostics['labs'][i]['created']
                    delta = epoch_time_now - created_seconds
                    days = int(delta // 86400)
                    hours = int(delta // 3600 % 24)
                    minutes = int(delta // 60 % 60)
                    seconds = int(delta % 60)
                    uptime = str(days) + ' Days, ' + str(hours) + ' Hrs, ' + str(minutes) + ' Mins, ' + str(seconds) + ' Secs'
                    lab_string += ' -  Lab Id: ' + i + ' Uptime: ' + uptime + '\n'
                if labs_flag:
                    on_server = True
                    server_name += lab_string
            if on_server:
                results_message += server_name
        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}
    """END VIRL LIST ALL LABS"""

    """START VIRL LIST USERS"""
    if activity.get('text') == 'VIRL list users':
        results_message = ''
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for virl_server in virl_servers:
            on_server = False
            server_name = '\n***' + virl_server + '***\n'
            virl = VIRL(CONFIG.VIRL_USERNAME, CONFIG.VIRL_PASSWORD, virl_server)
            # Get bearer token
            if not await virl.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl.status_code) + ' ' + virl.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue

            if not await virl.get_users():
                server_name += 'Error accessing server ' + virl_server + ': ' + str(virl.status_code) + ' ' + virl.users.get('description', '')
            else:
                for key in virl.users:
                    server_name += ' - ' + key + '\n'
            results_message += server_name

        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}
    """END VIRL LIST USERS"""

    """START VIRL LIST MY LABS"""
    if activity.get('text') == 'VIRL list my labs':
        results_message = ''
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        epoch_time_now = int(time.time())
        for virl_server in virl_servers:
            labs_flag = False
            server_name = '\n***' + virl_server + '***\n'
            virl = VIRL(CONFIG.VIRL_USERNAME, CONFIG.VIRL_PASSWORD, virl_server)
            # Get bearer token
            if not await virl.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl.status_code) + ' ' + virl.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue

            if not await virl.get_diagnostics():
                server_name += 'Error accessing server ' + virl_server + ': ' + str(virl.status_code) + ' ' + virl.diagnostics.get('description', '')
            else:
                labs = virl.diagnostics['user_roles']['labs_by_user'].get(user_and_domain[0], [])
                for lab in labs:
                    created_seconds = virl.diagnostics['labs'][lab]['created']
                    labs_flag = True
                    delta = epoch_time_now - created_seconds
                    days = int(delta // 86400)
                    hours = int(delta // 3600 % 24)
                    minutes = int(delta // 60 % 60)
                    seconds = int(delta % 60)
                    uptime = str(days) + ' Days, ' + str(hours) + ' Hrs, ' + str(minutes) + ' Mins, ' + str(seconds) + ' Secs'

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
        return {'status_code': 200}
    """END VIRL LIST MY LABS"""

    """START VIRL SHOW SERVER UTILIZATION"""
    if activity.get('text') == 'VIRL show server utilization':
        results_message = ''
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for virl_server in virl_servers:
            server_name = '\n***' + virl_server + '***\n'
            virl = VIRL(CONFIG.VIRL_USERNAME, CONFIG.VIRL_PASSWORD, virl_server)
            # Get bearer token
            if not await virl.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl.status_code) + ' ' + virl.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue

            if not await virl.get_system_status():
                server_name += 'Error accessing server ' + virl_server + ': ' + str(virl.status_code) + ' ' + virl.system_status.get('description', '')
            else:
                cpu = round(virl.system_status['clusters']['cluster_1']['high_level_drivers']['compute_1']['cpu']['percent'])
                memory = round(virl.system_status['clusters']['cluster_1']['high_level_drivers']['compute_1']['memory']['used'] / virl.system_status['clusters']['cluster_1']['high_level_drivers']['compute_1']['memory']['total'] * 100)

                server_name += ' -  CPU: ' + str(cpu) + '% Memory: ' + str(memory) + '%\n'
                results_message += server_name
        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}
    """END VIRL SHOW SERVER UTILIZATION"""

    """START VIRL EXTEND LAB"""
    if re.search('^VIRL extend lab .*', activity.get('text')):
        temp = activity.get('text').split('lab')
        lab = temp[1].strip()
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB]
            posts = db[CONFIG.MONGO_COLLECTIONS]
            query_lab_filter = {'user_id': activity.get('sender', ''),
                                'lab_id': lab}
            result = posts.find(query_lab_filter)
            epoch_time_now = int(time.time())
            doc = posts.find_one_and_update(query_lab_filter, {'$set': {'warning_date': epoch_time_now, 'renewal_flag': True}})

        if not doc:
            results_message = 'Not able to find lab: ' + lab
        else:
           results_message = lab + ' Successfully extended'

        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text=results_message,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}
    """END VIRL EXTEND LAB"""

    """START VIRL DELETE ACCOUNT DIALOGUE"""
    if activity.get('text') == 'VIRL delete account':
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        card_file = './cards/delete_account_get_password.json'
        with open(f'{card_file}') as fp:
            text = fp.read()
        card = json.loads(text)

        # If group then send a DM with a card
        if activity.get('roomType', '') == 'group':
            message = dict(text='Delete VIRL Account',
                           toPersonId=activity['sender'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            result = await webex.post_message_to_webex(message)
            print('\n')
            print(result.data)
            print(result.status_code)
            print(result.data['roomId'])
            print('\n')
            message = dict(text="I've direct messaged you. Let's continue this request in private.",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            activity['roomId'] = result.data['roomId']
        # if direct, send a card to the same room
        else:
            message = dict(text='Delete VIRL Account',
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
                                'dialogue_name': 'virl_delete_account',
                                'dialogue_step': 1,
                                'dialogue_max_steps': 2,
                                'dialogue_data': [],
                                'card_dialogue_index': 'virl_delete_account',
                                'card_feature_index': 'virl'}
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
            except Exception as e:
                print('Failed to connect to DB')
        return {'status_code': 200}
    if activity.get('dialogue_name') == 'virl_delete_account' and activity.get('dialogue_step') == 1:
        results_message = ''
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for virl_server in virl_servers:
            # In case a new dialogue has been entered, send msg, and cancel old dialogue
            try:
                virl_user = VIRL(user_and_domain[0], activity['inputs']['virl_password'], virl_server)
            except:
                message = dict(text='I thought we were talking about account deletion. Please send a new command',
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                # Remove dialogue from DB
                with pymongo.MongoClient(mongo_url) as client:
                    db = client[CONFIG.MONGO_DB_ACTIVITY]
                    posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                    query_lab_filter = {'sender': activity['sender'],
                                        'roomId': activity['roomId'],
                                        'dialogue_name': 'virl_delete_account'}
                    try:
                        r = posts.delete_one(query_lab_filter)
                    except Exception as e:
                        print('Failed to connect to DB')

                return {'status_code': 200}
            # Get bearer token
            virl_admin = VIRL(CONFIG.VIRL_USERNAME, CONFIG.VIRL_PASSWORD, virl_server)
            if not await virl_admin.get_token():
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl_admin.status_code) + ' ' + virl_admin.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                return {'status_code': 500}
            # If the user is not there, the below won't work
            if not await virl_user.get_token():
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl_user.status_code) + ' ' + virl_user.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue

            await virl_admin.list_user_lab_ids(user_and_domain[0])
            for lab in virl_admin.user_lab_ids:
                if not await virl_user.stop_lab(lab):
                    print('stop lab')
                    print(str(virl_user.status_code))
                    print(virl_user.result.get('description', ''))
                if not await virl_user.wipe_lab(lab):
                    print('wipe lab')
                    print(str(virl_user.status_code))
                    print(virl_user.result.get('description', ''))
                if not await virl_user.delete_lab(lab):
                    print('delete lab')
                    print(str(virl_user.status_code))
                    print(virl_user.result.get('description', ''))

            if not await virl_admin.delete_user(username_webex=user_and_domain[0]):
                results_message += ' - ' + virl_server + ' Fail: ' + str(virl_admin.status_code) + ' ' + virl_admin.result.get('description', '') + '\n'
            else:
                results_message += ' - ' + virl_server + ' Success! \n'

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
                                'dialogue_name': 'virl_delete_account'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                print('Failed to connect to DB')

        return {'status_code': 200}
    """END VIRL DELETE ACCOUNT DIALOGUE"""

    """START VIRL STOP LAB DIALOGUE"""
    if activity.get('text') == 'VIRL stop lab':
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        card_file = './cards/virl_stop_lab_get_password.json'
        with open(f'{card_file}') as fp:
            text = fp.read()
        card = json.loads(text)

        # If group then send a DM with a card
        if activity.get('roomType', '') == 'group':
            message = dict(text='Stop VIRL lab',
                           toPersonId=activity['sender'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            result = await webex.post_message_to_webex(message)

            message = dict(text="I've direct messaged you. Let's continue this stop lab request in private.",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            activity['roomId'] = result.data['roomId']
        # if direct, send a card to the same room
        else:
            message = dict(text='Stop VIRL lab',
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
                                'dialogue_name': 'virl_stop_lab',
                                'dialogue_step': 1,
                                'dialogue_max_steps': 2,
                                'dialogue_data': [],
                                'card_dialogue_index': 'virl_stop_lab',
                                'card_feature_index': 'virl'}
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
            except Exception as e:
                print('Failed to connect to DB')
        return {'status_code': 200}
    if activity.get('dialogue_name') == 'virl_stop_lab' and activity.get('dialogue_step') == 1:
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        running_labs_for_card = ''
        for virl_server in virl_servers:
            try:
                virl_user = VIRL(user_and_domain[0], activity['inputs']['virl_password'], virl_server)
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
                                        'dialogue_name': 'virl_stop_lab'}
                return {'status_code': 200}
            # Get bearer token
            if not await virl_user.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl_user.status_code) + ' ' + virl_user.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            # list the current users labs
            if not await virl_user.get_user_labs():
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl_user.status_code) + ' ' + virl_user.user_labs.get('description', ''),
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            lab_details = list()
            for lab in virl_user.user_labs:
                if await virl_user.get_user_lab_details(lab):
                    lab_details.append(virl_user.user_lab_details)
            final = ''
            running_labs = False
            if lab_details:
                lab_choices_string = '{"type": "TextBlock","text": "' + virl_server + '"},' + '{"type": "Input.ChoiceSet","id": "' + virl_server + '","style": "expanded","value": "1","choices": ['
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
            with open('cards/virl_stop_lab_choices.json') as file_:
                template = Template(file_.read())
            card = template.render(lab_choices=running_labs_for_card)
            card_json = json.loads(card)
            message = dict(text='Stop VIRL lab',
                           roomId=activity['roomId'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card_json}])
            result = await webex.post_message_to_webex(message)
            print('\n')
            print(result.data)
            print(result.status_code)
            print('\n')

            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                try:
                    doc = posts.find_one_and_update(
                        {'id': activity['id']},
                        {'$set': {'dialogue_step': 2,
                                  'card_dialogue_index': 'virl_stop_lab_choices',
                                  'virl_password': activity['inputs']['virl_password']}
                         }
                    )
                except Exception as e:
                    print('Failed to connect to DB')
            return {'status_code': 200}
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
                                    'dialogue_name': 'virl_stop_lab'}
                try:
                    r = posts.delete_one(query_lab_filter)
                except Exception as e:
                    print('Failed to connect to DB')

            return {'status_code': 200}
    if activity.get('card_dialogue_index') == 'virl_stop_lab_choices' and activity.get('dialogue_step') == 2:
        results_message = ''
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for virl_server in virl_servers:
            if activity['inputs'].get(virl_server):
                virl_user = VIRL(user_and_domain[0], activity['virl_password'], virl_server)
                # If the user is not there, the below won't work
                if not await virl_user.get_token():
                    message = dict(
                        text='Error accessing server ' + virl_server + ': ' + str(virl_user.status_code) + ' ' + virl_user.bearer_token,
                        roomId=activity['roomId'],
                        attachments=[])
                    await webex.post_message_to_webex(message)
                    continue
                labs_list = activity['inputs'].get(virl_server).split(',')
                for lab in labs_list:
                    if not await virl_user.stop_lab(lab):
                        print('stop lab')
                        print(str(virl_user.status_code))
                        print(virl_user.result.get('description', ''))
                        results_message += ' - ' + virl_server + ' Fail: ' + str(
                            virl_user.status_code) + ' ' + virl_user.result.get('description', '') + '\n'
                    else:
                        results_message += ' - ' + virl_server + ' Lab Id: ' + lab + ' Stopped!' + '\n'

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
                                'dialogue_name': 'virl_stop_lab'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                print('Failed to connect to DB')

        return {'status_code': 200}
    """ END VIRL STOP LAB DIALOGUE """

    """START VIRL DELETE LAB DIALOGUE"""
    if activity.get('text') == 'VIRL delete lab':
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        card_file = './cards/virl_delete_lab_get_password.json'
        with open(f'{card_file}') as fp:
            text = fp.read()
        card = json.loads(text)

        # If group then send a DM with a card
        if activity.get('roomType', '') == 'group':
            message = dict(text='Stop VIRL lab',
                           toPersonId=activity['sender'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card}])
            result = await webex.post_message_to_webex(message)
            # Now roomId is result.data['roomId']
            print(result.status_code)
            print(result.data['roomId'])
            print('\n')
            message = dict(text="I've direct messaged you. Let's continue this stop lab request in private.",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            activity['roomId'] = result.data['roomId']
        # if direct, send a card to the same room
        else:
            message = dict(text='Delete VIRL lab',
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
                               'dialogue_name': 'virl_delete_lab',
                               'dialogue_step': 1,
                               'dialogue_max_steps': 2,
                               'dialogue_data': [],
                               'card_dialogue_index': 'virl_delete_lab',
                               'card_feature_index': 'virl'}
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
            except Exception as e:
                print('Failed to connect to DB')
        return {'status_code': 200}
    if activity.get('dialogue_name') == 'virl_delete_lab' and activity.get('dialogue_step') == 1:
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        labs_for_card = ''
        for virl_server in virl_servers:
            try:
                virl_user = VIRL(user_and_domain[0], activity['inputs']['virl_password'], virl_server)
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
                                        'dialogue_name': 'virl_delete_lab'}
                return {'status_code': 200}

            # Get bearer token
            if not await virl_user.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl_user.status_code) + ' ' + virl_user.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            # list the current users labs
            if not await virl_user.get_user_labs():
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl_user.status_code) + ' ' + virl_user.user_labs.get('description', ''),
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            lab_details = list()
            for lab in virl_user.user_labs:
                if await virl_user.get_user_lab_details(lab):
                    lab_details.append(virl_user.user_lab_details)
            final = ''
            if lab_details:
                lab_choices_string = '{"type": "TextBlock","text": "' + virl_server + '"},' + '{"type": "Input.ChoiceSet","id": "' + virl_server + '","style": "expanded","value": "1","choices": ['
                for i in lab_details:
                    temp_string = i['lab_title'] + '   Created: ' + i['created']
                    temp_details = i['id']
                    lab_choices_string += '{"title": "' + temp_string + '","value": "' + temp_details + '"},'
                    final = lab_choices_string[:-1]
                    final += '],"isMultiSelect": true},'

                labs_for_card += final
        if labs_for_card:
            with open('cards/virl_delete_lab_choices.json') as file_:
                template = Template(file_.read())
            card = template.render(lab_choices=labs_for_card)
            card_json = json.loads(card)
            message = dict(text='VIRL delete lab',
                           roomId=activity['roomId'],
                           attachments=[{'contentType': 'application/vnd.microsoft.card.adaptive', 'content': card_json}])
            result = await webex.post_message_to_webex(message)
            # This needs to be an update
            with pymongo.MongoClient(mongo_url) as client:
                db = client[CONFIG.MONGO_DB_ACTIVITY]
                posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
                try:
                    doc = posts.find_one_and_update(
                        {'id': activity['id']},
                        {'$set': {'dialogue_step': 2,
                                  'card_dialogue_index': 'virl_delete_lab_choices',
                                  'virl_password': activity['inputs']['virl_password']}
                         }
                    )
                except Exception as e:
                    print('Failed to connect to DB')
            return {'status_code': 200}
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
                                    'dialogue_name': 'virl_delete_lab'}
                try:
                    r = posts.delete_one(query_lab_filter)
                except Exception as e:
                    print('Failed to connect to DB')

            return {'status_code': 200}
    if activity.get('card_dialogue_index') == 'virl_delete_lab_choices' and activity.get('dialogue_step') == 2:
        results_message = ''
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for virl_server in virl_servers:
            if activity['inputs'].get(virl_server):
                virl_user = VIRL(user_and_domain[0], activity['virl_password'], virl_server)
                # If the user is not there, the below won't work
                if not await virl_user.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                    message = dict(
                        text='Error accessing server ' + virl_server + ': ' + str(virl_user.status_code) + ' ' + virl_user.bearer_token,
                        roomId=activity['roomId'],
                        attachments=[])
                    await webex.post_message_to_webex(message)
                    continue
                labs_list = activity['inputs'].get(virl_server).split(',')
                for lab in labs_list:
                    if not await virl_user.stop_lab(lab):
                        print('stop lab')
                        print(str(virl_user.status_code))
                        print(virl_user.result.get('description', ''))
                    if not await virl_user.wipe_lab(lab):
                        print('wipe lab')
                        print(str(virl_user.status_code))
                        print(virl_user.result.get('description', ''))
                    if not await virl_user.delete_lab(lab):
                        print('delete lab')
                        print(str(virl_user.status_code))
                        print(virl_user.result.get('description', ''))
                        results_message += ' - ' + virl_server + ' Fail: ' + str(
                            virl_user.status_code) + ' ' + virl_user.result.get('description', '') + '\n'
                    else:
                        results_message += ' - ' + virl_server + ' Lab Id: ' + lab + ' Deleted!' + '\n'

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
                                'dialogue_name': 'virl_delete_lab'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                print('Failed to connect to DB')

        return {'status_code': 200}
    """ END VIRL DELETE LAB DIALOGUE """

    """START VIRL LIST MY LAB DETAILS DIALOGUE"""
    if activity.get('text') == 'VIRL list my lab details':
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
            print('\n')
            print(result.data)
            # Now roomId is result.data['roomId']
            print(result.status_code)
            print(result.data['roomId'])
            print('\n')
            message = dict(text="I've direct messaged you. Let's continue this request in private.",
                           roomId=activity['roomId'],
                           attachments=[])
            await webex.post_message_to_webex(message)
            activity['roomId'] = result.data['roomId']
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
                                'dialogue_name': 'virl_list_lab_details',
                                'dialogue_step': 1,
                                'dialogue_max_steps': 2,
                                'dialogue_data': [],
                                'card_dialogue_index': 'virl_list_lab_details',
                                'card_feature_index': 'virl'}
            try:
                post_id = posts.insert_one(dialogue_record).inserted_id
            except Exception as e:
                print('Failed to connect to DB')
        return {'status_code': 200}
    if activity.get('dialogue_name') == 'virl_list_lab_details' and activity.get('dialogue_step') == 1:
        results_message = ''
        user_and_domain = activity['sender_email'].split('@')
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        for virl_server in virl_servers:
            try:
                virl_user = VIRL(user_and_domain[0], activity['inputs']['virl_password'], virl_server)
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
                                        'dialogue_name': 'virl_list_lab_details'}
                return {'status_code': 200}
            # Get bearer token
            # If the user is not there, the below won't work
            if not await virl_user.get_token():  # {'description': 'User already exists: stmosher.', 'code': 422}
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl_user.status_code) + ' ' + virl_user.bearer_token,
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            # list the current users labs
            if not await virl_user.get_user_labs():
                message = dict(text='Error accessing server ' + virl_server + ': ' + str(virl_user.status_code) + ' ' + virl_user.user_labs.get('description', ''),
                               roomId=activity['roomId'],
                               attachments=[])
                await webex.post_message_to_webex(message)
                continue
            lab_details = list()
            for lab in virl_user.user_labs:
                if await virl_user.get_user_lab_details(lab):
                    lab_details.append(virl_user.user_lab_details)

            if lab_details:
                results_message += '\n' + virl_server + ' labs are: \n'
                for lab in lab_details:
                    results_message += ' - Lab Title: ' + lab['lab_title'] + ' Lab Id:: ' + lab['id'] + ' Created: ' + lab['created'] + ' State: ' + lab['state'] + '\n'
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
                                'dialogue_name': 'virl_list_lab_details'}
            try:
                r = posts.delete_one(query_lab_filter)
            except Exception as e:
                print('Failed to connect to DB')

        return {'status_code': 200}
    """END VIRL LIST MY LAB DETAILS DIALOGUE"""

    """START CATCH ALL"""
    if activity.get('roomType') == 'group':
        message = dict(
            text='"' + activity['text'] + '?"' + " I'm sorry. I don't understand. Please reply " + "**@" +
                 activity['bot_name'] + " help** to see my available commands",
            roomId=activity['roomId'],
            attachments=[])
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}
    else:
        message = dict(text='"' + activity['text'] + '?"' + " I'm sorry. I don't understand. Please reply 'help' to see my available commands",
                       roomId=activity['roomId'],
                       attachments=[])
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}
    """END CATCH ALL"""
