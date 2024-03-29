#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import aiohttp
import requests
from webexteamssdk import WebexTeamsAPI


class WebExClient:
    """
    Methods to communication with WebEx APIs
    """

    def __init__(self, webex_bot_token=None):
        if not webex_bot_token:
            raise ValueError("bot_token is required")
        self.webex_bot_token = webex_bot_token
        self.logging_message = "This is the aiohttp webex Client session"
        self.logging_webex_message = "Exception retrieving WebEx message attachment"
        self.content_type = "application/json"
        self.bearer_text = "Bearer "

    async def post_message_to_webex(self, message=None):
        if not message:
            return None
        headers = {
            "Content-Type": self.content_type,
            "Authorization": self.bearer_text + self.webex_bot_token,
        }

        post_data = self.dict_from_items_with_values(
            roomId=message.get("roomId"),
            markdown=message.get("text"),
            attachments=message.get("attachments"),
            toPersonId=message.get("toPersonId"),
            parentId=message.get("parentId"),
            files=message.get("files"),
        )
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="POST",
                    url="https://api.ciscospark.com/v1/messages",
                    headers=headers,
                    data=json.dumps(post_data),
                ) as res:
                    response_content = await res.json()
                    logging.debug(
                        "WebEx POST message response_content: %s", response_content
                    )
                    return response_content
            except Exception:
                logging.info("Exception posting WebEx message")
                return {}

    async def send_message_with_file(self, message=None):
        if not message:
            return None

        api = WebexTeamsAPI(access_token=self.webex_bot_token)
        api.messages.create(
            roomId=message.get("roomId"),
            markdown=message.get("text"),
            files=message.get("files"),
        )

    async def edit_message(self, message_id, message, room_id):
        URL = f"https://webexapis.com/v1/messages/{message_id}"

        headers = {
            "Authorization": "Bearer " + self.webex_bot_token,
            "Content-type": "application/json;charset=utf-8",
        }
        post_data = {"roomId": room_id, "markdown": message}
        response = requests.put(URL, json=post_data, headers=headers)
        if response.status_code == 200:
            logging.debug("Message updated successfully")
        else:
            logging.debug(
                "Status code: %s Error message: %s", response.status_code, response.text
            )

    async def get_message_details(self, message_id):
        api_url = "https://api.ciscospark.com/v1/messages/" + message_id
        headers = {
            "Content-Type": self.content_type,
            "Authorization": self.bearer_text + self.webex_bot_token,
        }
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=api_url, headers=headers
                ) as res:
                    response_content = await res.json()
                    return response_content
            except Exception:
                logging.info("Exception retrieving WebEx message")
                return {}

    async def get_card_attachment(self, message_id):
        api_url = "https://api.ciscospark.com/v1/attachment/actions/" + message_id
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": self.bearer_text + self.webex_bot_token,
        }
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=api_url, headers=headers
                ) as res:
                    response_content = await res.json()
                    return response_content
            except Exception:
                logging.info(self.logging_webex_message)
                return {}

    async def delete_message(self, message_id):
        api_url = "https://api.ciscospark.com/v1/messages/" + message_id
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": self.bearer_text + self.webex_bot_token,
        }
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="DELETE", url=api_url, headers=headers
                ) as res:
                    response_content = await res.json()
                    return response_content
            except Exception:
                logging.info(self.logging_webex_message)
                return {}

    async def get_room_memberships(self, room_id, person_id):
        api_url = (
            "https://api.ciscospark.com/v1/memberships?roomId="
            + room_id
            + "&personId="
            + person_id
        )
        headers = {
            "Content-Type": self.content_type,
            "Authorization": self.bearer_text + self.webex_bot_token,
        }
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            logging.debug("%s %s", self.logging_message, session)
            try:
                async with session.request(
                    method="GET", url=api_url, headers=headers
                ) as res:
                    response_content = await res.json()
                    return response_content
            except Exception:
                logging.info(self.logging_webex_message)
                return {}

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
        return [i.get("personId") for i in content.get("items")]
