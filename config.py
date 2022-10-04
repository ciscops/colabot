# -*- coding: utf-8 -*-

import os
from webbrowser import get


class DefaultConfig:
    """Bot Configuration"""

    WEB_PORT = os.environ.get("WEB_PORT", "3000")
    BOT_ID = os.environ.get("BOT_ID", "abc12345")
    BOT_NAME = os.environ.get("BOT_NAME", "rob")
    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "123456789")
    DIALOGUE_TIMEOUT = os.environ.get("DIALOGUE_TIMEOUT", "30")
    SECRET = os.environ.get("SECRET", "abc")
    MONGO_INITDB_ROOT_USERNAME = os.environ.get(
        "MONGO_INITDB_ROOT_USERNAME", "db_admin"
    )
    MONGO_INITDB_ROOT_PASSWORD = os.environ.get(
        "MONGO_INITDB_ROOT_PASSWORD", "password123"
    )
    MONGO_SERVER = os.environ.get("MONGO_SERVER", "server.example.com")
    MONGO_PORT = os.environ.get("MONGO_PORT", "27017")
    MONGO_DB_ACTIVITY = os.environ.get("MONGO_DB_ACTIVITY", "bot_activity_db")
    MONGO_COLLECTIONS_ACTIVITY = os.environ.get(
        "MONGO_COLLECTIONS_ACTIVITY", "bot_activity_collection"
    )
    SERVER_LIST = os.environ.get("SERVER_LIST", "cml.example.com")
    CML_USERNAME = os.environ.get("CML_USERNAME", "admin")
    CML_PASSWORD = os.environ.get("CML_PASSWORD", "adminpwd")
    APPROVED_ORG_DOMAINS = os.environ.get("APPROVED_ORG_DOMAINS", "example.com")
    MONGO_DB = os.environ.get("MONGO_DB", "bot_db")
    MONGO_COLLECTIONS = os.environ.get("MONGO_COLLECTIONS", "bot_collections")
    AUTHORIZED_ROOMS = os.environ.get("AUTHORIZED_ROOMS", "")
    AWX_USERNAME = os.environ.get("AWX_USERNAME", "")
    AWX_PASSWORD = os.environ.get("AWX_PASSWORD", "")
    NLP_SERVER = os.environ.get("NLP_SERVER", "nlp-server.example.com")
    NLP_SECRET = os.environ.get("NLP_SECRET", "xxxx")
    VCENTER_SERVER = os.environ.get("VCENTER_SERVER", "vcenter.example.com")
    AWX_SERVER = os.environ.get("AWX_SERVER", "xxxx")
    ADMINISTRATORS = os.environ.get(
        "ADMINISTRATORS", "admin1@domain.com,admin2@domain.com"
    )
    AWS_REGION = os.environ.get("AWS_REGION", "xxxx")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "xxxx")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "xxxx")
    AWS_REGION_COLAB = os.environ.get("AWS_REGION_COLAB", "xxxx")
    AWS_ACCESS_KEY_ID_COLAB = os.environ.get("AWS_ACCESS_KEY_ID_COLAB", "xxxx")
    AWS_SECRET_ACCESS_KEY_COLAB = os.environ.get("AWS_SECRET_ACCESS_KEY_COLAB", "xxxx")
    AWX_DECRYPT_KEY = os.environ.get("COLABOT_SECRET", "xxxx")
