import os


class Config(object):
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

    APP_ID = int(os.environ.get("APP_ID", 12345))

    API_HASH = os.environ.get("API_HASH", "")
	
    BOT_USERNAME = os.environ.get("BOT_USERNAME")
	
    BOT_OWNER = int(os.environ.get("BOT_OWNER"))
	
    DATABASE_URL = os.environ.get("DATABASE_URL")
