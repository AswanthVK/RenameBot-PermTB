import os

class Config(object):

    # get a token from @BotFather
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

    # The Telegram API things
    APP_ID = int(os.environ.get("APP_ID", 12345))
    API_HASH = os.environ.get("API_HASH")
    # Get these values from my.telegram.org

    # Array to store users who are authorized to use the bot
    AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "").split())

    # Ban Unwanted Members..
    BANNED_USERS = []

    # the download location, where the HTTP Server runs
    DOWNLOAD_LOCATION = "./DOWNLOADS"

    # Telegram maximum file upload size
    TG_MAX_FILE_SIZE = 2097152000

    # chunk size that should be used with requests
    CHUNK_SIZE = 128

    FORCE_SUB = os.environ.get("FORCE_SUB", "") if os.environ.get("FORCE_SUB", "") else None

    # Update channel for Force Subscribe
    UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "")

    SESSION_NAME = os.environ.get("SESSION_NAME", "NewRename_Bot")
  
    # Database url
    DB_URI = os.environ.get("DATABASE_URL", "")

    TIME_GAP = os.environ.get("TIME_GAP", "")
 
    TIME_GAP_STORE = {}
  
    TRACE_CHANNEL = os.environ.get("TRACE_CHANNEL", "")

    MONGODB_URI = os.environ.get("MONGODB_URI", False)

    BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", False))
  
    MAX_VIDEOS = int(os.environ.get("MAX_VIDEOS", 5))
     

    
