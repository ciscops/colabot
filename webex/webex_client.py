#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import aiohttp
import logging


class WebExClient:
    """
    Methods to communication with WebEx APIs
    """
    def __init__(self, webex_bot_token=None):
        if not webex_bot_token:
            raise Exception("bot_token is required")
        self.webex_bot_token = webex_bot_token

    async def post_message_to_webex(self, message=None):
        if not message:
            return None
        headers = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + self.webex_bot_token
        }

        post_data = self.dict_from_items_with_values(
            roomId=message.get('roomId'),
            markdown=message.get('text'),
            attachments=message.get('attachments'),
            toPersonId=message.get('toPersonId'),
            parentId=message.get('parentId'),
            files=message.get('files'),
        )
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), )
        response_content = {}
        try:
            async with session.request(method="POST", url='https://api.ciscospark.com/v1/messages',
                                       headers=headers,
                                       data=json.dumps(post_data)) as res:
                response_content = await res.json()
                await session.close()
                return response_content
        except Exception as e:
            logging.warning(e)
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return response_content

    async def get_message_details(self, message_id):
        api_url = 'https://api.ciscospark.com/v1/messages/' + message_id
        headers = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + self.webex_bot_token
        }
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), )
        response_content = {}
        try:
            async with session.request(method="GET", url=api_url, headers=headers) as res:
                response_content = await res.json()
                await session.close()
                return response_content
        except Exception as e:
            logging.warning(e)
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return response_content

    async def get_card_attachment(self, message_id):
        api_url = 'https://api.ciscospark.com/v1/attachment/actions/' + message_id
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            "Authorization": "Bearer " + self.webex_bot_token
        }
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), )
        response_content = {}
        try:
            async with session.request(method="GET", url=api_url, headers=headers) as res:
                response_content = await res.json()
                await session.close()
                return response_content
        except Exception as e:
            logging.warning(e)
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return response_content

    async def delete_message(self, message_id):
        api_url = 'https://api.ciscospark.com/v1/messages/' + message_id
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            "Authorization": "Bearer " + self.webex_bot_token
        }
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), )
        response_content = {}
        try:
            async with session.request(method="DELETE", url=api_url, headers=headers) as res:
                response_content = await res.json()
                await session.close()
                return response_content
        except Exception as e:
            logging.warning(e)
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return response_content

    async def get_room_memberships(self, room_id, person_id):
        api_url = 'https://api.ciscospark.com/v1/memberships?roomId=' + room_id + '&personId=' + person_id
        headers = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + self.webex_bot_token
        }
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), )
        try:
            async with session.request(method="GET", url=api_url, headers=headers) as res:
                await session.close()
                return res.status
        except Exception as e:
            logging.warning(e)
            try:
                await session.close()
            except Exception as e:
                logging.warning(e)
            return 500

    @staticmethod
    def dict_from_items_with_values(*dictionaries, **items):
        """Creates a dict with the inputted items; pruning any that are `None`.
        Args:
            *dictionaries(dict): Dictionaries of items to be pruned and included.
            **items: Items to be pruned and included.
        Returns:
            dict: A dictionary containing all of the items with a 'non-None' value.
        """
        dict_list = list(dictionaries)
        dict_list.append(items)
        result = {}
        for d in dict_list:
            for key, value in d.items():
                if value is not None:
                    result[key] = value
        return result

    @staticmethod
    async def create_user_id_list_from_room_membership_content(content):
        return [i.get('personId') for i in content.get('items')]
