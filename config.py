# -*- coding: utf-8 -*-

import os


class DefaultConfig:
    """ Bot Configuration """
    WEB_PORT = os.environ.get('WEB_PORT', '3000')
    BOT_ID = os.environ.get('BOT_ID', 'abc12345')
    BOT_NAME = os.environ.get('BOT_NAME', 'rob')
    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '123456789')
    DIALOGUE_TIMEOUT = os.environ.get('DIALOGUE_TIMEOUT', '30')
    SECRET = os.environ.get('SECRET', 'abc')
    MONGO_INITDB_ROOT_USERNAME = os.environ.get('MONGO_INITDB_ROOT_USERNAME', 'db_admin')
    MONGO_INITDB_ROOT_PASSWORD = os.environ.get('MONGO_INITDB_ROOT_PASSWORD', 'password123')
    MONGO_SERVER = os.environ.get('MONGO_SERVER', 'server.example.com')
    MONGO_PORT = os.environ.get('MONGO_PORT', '27017')
    MONGO_DB_ACTIVITY = os.environ.get('MONGO_DB_ACTIVITY', 'bot_activity_db')
    MONGO_COLLECTIONS_ACTIVITY = os.environ.get('MONGO_COLLECTIONS_ACTIVITY', 'bot_activity_collection')
    SERVER_LIST = os.environ.get('SERVER_LIST', 'cml.example.com')
    VIRL_USERNAME = os.environ.get('VIRL_USERNAME', 'admin')
    VIRL_PASSWORD = os.environ.get('VIRL_PASSWORD', 'adminpwd')
    APPROVED_ORG_DOMAINS = os.environ.get('APPROVED_ORG_DOMAINS', 'example.com')
    MONGO_DB = os.environ.get('MONGO_DB', 'bot_db')
    MONGO_COLLECTIONS = os.environ.get('MONGO_COLLECTIONS', 'bot_collections')
    AUTHORIZED_ROOMS = os.environ.get('AUTHORIZED_ROOMS', '')