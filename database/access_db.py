# (c) @AbirHasan2005

from sample_config import Config
from database.newdatabase import Database

db = Database(Config.MONGODB_URI, Config.SESSION_NAME)
