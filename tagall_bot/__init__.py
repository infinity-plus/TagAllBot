import logging
from os import environ

from telegram.ext import Dispatcher, Updater
from telethon.sync import TelegramClient

from tagall_bot.sql.roles import get_users, sudo_users, tag_users

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


LOGGER = logging.getLogger(__name__)

TOKEN = environ.get("TOKEN", "")

try:
    OWNER_ID = int(environ.get("OWNER_ID", ""))
except ValueError:
    raise ValueError("Your OWNER_ID env variable is not a valid integer.")

try:
    SUDO_USERS = {int(x) for x in environ.get("SUDO_USERS", "").split()}
except ValueError:
    raise ValueError("Your sudo users list does not contain valid integers.")

try:
    SUDO_GROUPS = {int(x) for x in environ.get("SUDO_GROUPS", "").split()}
except ValueError:
    raise ValueError("Your sudo groups list does not contain valid integers.")

try:
    DND_USERS = {int(x) for x in environ.get("DND_USERS", "").split()}
except ValueError:
    raise ValueError("Your DND users list does not contain valid integers.")

try:
    API_ID = int(environ.get("API_ID", ""))
except ValueError:
    raise ValueError("Your API_ID is not a valid integer.")
API_HASH = environ.get("API_HASH", "")
WEBHOOK = bool(environ.get("WEBHOOK", False))
URL = environ.get("URL", "")  # Does not contain token
PORT = int(environ.get("PORT", 5000))

DB_URI = environ.get("DATABASE_URL")
SUDO_USERS.add(OWNER_ID)
SUDO_USERS.update(get_users(sudo_users), SUDO_GROUPS)
TAG_USERS = get_users(tag_users)

UPDATER: Updater = Updater(token=TOKEN)
DISPATCHER: Dispatcher = UPDATER.dispatcher
TELETHON_CLIENT = TelegramClient("tagall_bot", API_ID, API_HASH)
iter_participants = TELETHON_CLIENT.iter_participants
