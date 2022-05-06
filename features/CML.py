#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
import random
import logging
import aiohttp
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CML:
    def __init__(self, cml_username, cml_password, cml_server):
        self.cml_username = cml_username
        self.cml_password = cml_password
        self.url = "https://" + cml_server
        self.bearer_token = ""
        self.diagnostics = {}
        self.old_labs_results_list = []
        self.stop_result = ""
        self.wipe_result = ""
        self.delete_result = ""
        self.all_labs = []
        self.status_code = ""
        self.users = {}
        self.lab_nodes = []
        self.lab_int_addresses = {}
        self.user_labs = []
        self.user_lab_details = {}
        self.system_status = {}
        self.result = {}
        self.user_lab_ids = ""
        self.logging_message = "This is the aiohttp Client session"

    async def get_token(self):
        api_path = "/api/v0/authenticate"
        headers = {"Content-Type": "application/json"}
        u = self.url + api_path
        body = {"username": self.cml_username, "password": self.cml_password}
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="POST",
                    url=u,
                    headers=headers,
                    data=json.dumps(body),
                    ssl=False,
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        logging.debug("token response is 200")
                        self.status_code = res.status
                        self.bearer_token = response_content
                        return True
                    logging.debug("token response is %s", res.status)
                    self.status_code = res.status
                    self.bearer_token = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception getting token")
                self.status_code = 500
                return False

    async def get_users(self):
        api_path = "/api/v0/users"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.users = response_content
                        return True
                    self.status_code = res.status
                    self.users = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception getting users")
                self.status_code = 500
                return False

    async def get_diagnostics(self):
        api_path = "/api/v0/diagnostics"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        self.diagnostics = {}
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.diagnostics = response_content
                        return True
                    self.status_code = res.status
                    self.diagnostics = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception getting diagnostics")
                self.status_code = 500
                return False

    async def get_lab_nodes(self, lab_id):
        api_path = f"/api/v0/labs/{lab_id}/nodes"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.lab_nodes = response_content
                        return True
                    self.status_code = res.status
                    self.lab_nodes = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception getting lab_nodes")
                self.status_code = 500
                return False

    async def layer3_addresses(self, lab_id, node_id):
        api_path = f"/api/v0/labs/{lab_id}/nodes/{node_id}/layer3_addresses"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.lab_int_addresses = response_content
                        return True
                    self.status_code = res.status
                    self.lab_int_addresses = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception getting lab_int_addresses")
                self.status_code = 500
                return False

    async def get_user_labs(self):
        api_path = "/api/v0/labs"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.user_labs = response_content
                        return True
                    self.status_code = res.status
                    self.user_labs = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception getting user_labs")
                self.status_code = 500
                return False

    async def get_user_lab_details(self, lab_id):
        api_path = "/api/v0/labs/" + lab_id
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.user_lab_details = response_content
                        return True
                    self.status_code = res.status
                    self.user_lab_details = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception getting user_lab_details")
                self.status_code = 500
                return False

    async def get_system_status(self):
        api_path = "/api/v0/system_stats"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.system_status = response_content
                        return True
                    self.status_code = res.status
                    self.system_status = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception getting system_status")
                self.status_code = 500
                return False

    async def stop_lab(self, lab_id):
        api_path = "/api/v0/labs/" + lab_id + "/stop"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        self.result = {}
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="PUT", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.result = response_content
                        return True
                    self.status_code = res.status
                    self.result = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception stopping lab")
                self.status_code = 500
                return False

    async def wipe_lab(self, lab_id):
        api_path = "/api/v0/labs/" + lab_id + "/wipe"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        self.result = {}
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="PUT", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.result = response_content
                        return True
                    self.status_code = res.status
                    self.result = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception wiping lab")
                self.status_code = 500
                return False

    async def delete_lab(self, lab_id):
        api_path = "/api/v0/labs/" + lab_id
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        self.result = {}
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="DELETE", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.result = response_content
                        return True
                    self.status_code = res.status
                    self.result = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception deleting lab")
                self.status_code = 500
                return False

    async def change_password(self, username_webex, new_password):
        api_path = "/api/v0/users/" + username_webex + "/change_password"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        body = {"old_password": "", "new_password": new_password}
        u = self.url + api_path
        self.result = {}
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="PUT",
                    url=u,
                    headers=headers,
                    data=json.dumps(body),
                    ssl=False,
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.result = response_content
                        return True
                    self.status_code = res.status
                    self.result = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception changing password")
                self.status_code = 500
                return False

    async def add_user(self, username_webex, user_email, new_password):
        api_path = "/api/v0/users/" + username_webex
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        body = {
            "password": new_password,
            "fullname": user_email,
            "description": "",
            "roles": ["User"],
            "context": {},
        }
        u = self.url + api_path
        self.result = {}
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="POST",
                    url=u,
                    headers=headers,
                    data=json.dumps(body),
                    ssl=False,
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.result = response_content
                        return True
                    self.status_code = res.status
                    self.result = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception adding user")
                self.status_code = 500
                return False

    async def delete_user(self, username_webex):
        api_path = "/api/v0/users/" + username_webex
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "cache-control": "no-cache",
            "Authorization": "Bearer " + self.bearer_token,
        }
        u = self.url + api_path
        self.result = {}
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="DELETE", url=u, headers=headers, ssl=False
                ) as res:
                    response_content = await res.json()
                    if res.status == 200:
                        self.status_code = res.status
                        self.result = response_content
                        return True
                    self.status_code = res.status
                    self.result = response_content
                    return False
            except asyncio.CancelledError:
                logging.info("Exception adding user")
                self.status_code = 500
                return False

    async def list_user_lab_ids(self, username_webex):
        if await self.get_diagnostics():
            try:
                self.user_lab_ids = self.diagnostics["user_roles"]["labs_by_user"][
                    username_webex
                ]
            except KeyError:
                self.user_lab_ids = []

    @staticmethod
    def password_generator():
        pwd = ""
        length = 10
        lower = "abcdefghijklmnopqrstuvwxyz"
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        symbols = "!@#%-+"
        numbers = "0123456789"
        pos = lower + upper + symbols + numbers
        l = list(pos)
        random.shuffle(l)
        pos = "".join(l)
        for _ in range(0, length):
            rand = random.randint(0, len(pos) - 1)
            pwd += pos[rand]
        return pwd
