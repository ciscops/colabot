#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aiohttp
import json
import random
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CML:
    def __init__(self, cml_username, cml_password, cml_server):
        self.cml_username = cml_username
        self.cml_password = cml_password
        self.url = 'https://' + cml_server
        self.bearer_token = ''
        self.diagnostics = dict()
        self.old_labs_results_list = list()
        self.stop_result = ''
        self.wipe_result = ''
        self.delete_result = ''
        self.all_labs = list()
        self.status_code = ''

    async def get_token(self):
        api_path = '/api/v0/authenticate'
        headers = {
            'Content-Type': 'application/json'
        }
        u = self.url + api_path
        body = {'username': self.cml_username, 'password': self.cml_password}
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        try:
            async with session.request(method="POST", url=u,
                                       headers=headers,
                                       data=json.dumps(body), ssl=False) as res:
                response_content = {}

                response_content = await res.json()
                logging.debug('BELOW IS THE RESPONSE')
                logging.debug(response_content)
                logging.debug('BELOW IS THE STATUS CODE')
                logging.debug(res.status)
                if res.status != 200:
                    self.status_code = res.status
                    self.bearer_token = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.bearer_token = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.bearer_token = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.bearer_token = ''
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def get_users(self):
        api_path = '/api/v0/users'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        try:
            async with session.request(method="GET", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.users = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.users = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.users = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.users = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def get_diagnostics(self):
        api_path = '/api/v0/diagnostics'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        try:
            async with session.request(method="GET", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.diagnostics = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.diagnostics = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.diagnostics = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.diagnostics = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def get_lab_nodes(self, lab_id):
        api_path = f'/api/v0/labs/{lab_id}/nodes'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        try:
            async with session.request(method="GET", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = []
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.lab_nodes = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.lab_nodes = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.lab_nodes = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.lab_nodes = []
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def layer3_addresses(self, lab_id, node_id):
        api_path = f'/api/v0/labs/{lab_id}/nodes/{node_id}/layer3_addresses'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        try:
            async with session.request(method="GET", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.lab_int_addresses = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.lab_int_addresses = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.lab_int_addresses = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.lab_int_addresses = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def get_user_labs(self):
        api_path = '/api/v0/labs'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        try:
            async with session.request(method="GET", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = []
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.user_labs = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.user_labs = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.user_labs = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.user_labs = []
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def get_user_lab_details(self, lab_id):
        api_path = '/api/v0/labs/' + lab_id
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        try:
            async with session.request(method="GET", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.user_lab_details = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.user_lab_details = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.user_lab_details = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.user_lab_details = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def get_system_status(self):
        api_path = '/api/v0/system_stats'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        try:
            async with session.request(method="GET", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.system_status = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.system_status = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.system_status = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.system_status = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def stop_lab(self, lab_id):
        api_path = '/api/v0/labs/' + lab_id + '/stop'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300))
        try:
            async with session.request(method="PUT", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.result = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.result = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.result = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.result = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def wipe_lab(self, lab_id):
        api_path = '/api/v0/labs/' + lab_id + '/wipe'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300))
        try:
            async with session.request(method="PUT", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.result = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.result = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.result = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.result = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def delete_lab(self, lab_id):
        api_path = '/api/v0/labs/' + lab_id
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        try:
            async with session.request(method="DELETE", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.result = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.result = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.result = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.result = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def change_password(self, username_webex, new_password):
        api_path = '/api/v0/users/' + username_webex + '/change_password'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        body = {'old_password': '', 'new_password': new_password}
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        try:
            async with session.request(method="PUT", url=u,
                                       headers=headers, data=json.dumps(body),ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.result = response_content
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.result = response_content
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.result = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.result = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def add_user(self, username_webex, user_email, new_password):
        api_path = '/api/v0/users/' + username_webex
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        body = {'password': new_password,
                'fullname': user_email,
                'description': '',
                'roles': [
                    'User'
                ],
                'context': {}
                }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        try:
            async with session.request(method="POST", url=u,
                                       headers=headers, data=json.dumps(body),ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.result = response_content
                    logging.debug(response_content)
                    logging.debug(type(response_content))
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.result = response_content
                    logging.debug(response_content)
                    logging.debug(type(response_content))
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.result = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.result = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def delete_user(self, username_webex):
        api_path = '/api/v0/users/' + username_webex
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache",
            "Authorization": "Bearer " + self.bearer_token
        }
        u = self.url + api_path
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        try:
            async with session.request(method="DELETE", url=u,
                                       headers=headers, ssl=False) as res:
                response_content = {}
                response_content = await res.json()
                if res.status != 200:
                    self.status_code = res.status
                    self.result = response_content
                    logging.debug(response_content)
                    logging.debug(type(response_content))
                    await session.close()
                    return False
                else:
                    self.status_code = res.status
                    self.result = response_content
                    logging.debug(response_content)
                    logging.debug(type(response_content))
                    await session.close()
                    return True
        except aiohttp.ContentTypeError as e:
            logging.warning(e)
            self.status_code = 500
            self.result = response_content
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)
            self.status_code = 500
            self.result = {}
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return False

    async def list_user_lab_ids(self, username_webex):
        if await self.get_diagnostics():
            try:
                self.user_lab_ids = self.diagnostics['user_roles']['labs_by_user'][username_webex]
            except KeyError:
                self.user_lab_ids =[]

    @staticmethod
    def password_generator():
        pwd = ''
        length = 10
        lower = "abcdefghijklmnopqrstuvwxyz"
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        symbols = "!@#%-+"
        numbers = "0123456789"
        pos = lower + upper + symbols + numbers
        l = list(pos)
        random.shuffle(l)
        pos = ''.join(l)
        for i in range(0, length):
            rand = random.randint(0, len(pos) - 1)
            pwd += pos[rand]
        return pwd

if __name__ == '__main__':
    import asyncio
    import time

    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    my_username = ''
    my_password = ''
    async def check_get_token(my_username, my_password):
        cml_servers = ['cpn-rtp-cml4.ciscops.net',
                       'cpn-rtp-cml-stable3.ciscops.net',
                       'cpn-rtp-cml-test1.ciscops.net',
                       'cpn-rtp-cml-stable2.ciscops.net']
        for cml_server in cml_servers:
            print('\n\n\n' + cml_server)
            cml = CML(my_username, my_password, cml_server)
            print(await cml.get_token())
            if cml.status_code == 200:
                if not await cml.get_system_status():
                    print('Error accessing server ' + cml_server + ': ' + str(
                        cml.status_code) + ' ' + cml.system_status.get('description', ''))
                else:
                    cpu = round(
                        cml.system_status['clusters']['cluster_1']['high_level_drivers']['compute_1']['cpu']['percent'])
                    memory = round(
                        cml.system_status['clusters']['cluster_1']['high_level_drivers']['compute_1']['memory']['used'] /
                        cml.system_status['clusters']['cluster_1']['high_level_drivers']['compute_1']['memory'][
                            'total'] * 100)
                    print(' -  CPU: ' + str(cpu) + '% Memory: ' + str(memory) + '%\n')
            else:
                print('Error accessing server ' + cml_server + ': ' + str(
                    cml.status_code) + ' ' + cml.bearer_token)
                print(cml.bearer_token)

    s = time.perf_counter()
    asyncio.run(check_get_token(my_username, my_password))
    elapsed = time.perf_counter() - s
    print(f"executed in {elapsed:0.2f} seconds.")
