import logging
from os import environ

from ptbcontrib.roles import Roles, setup_roles
from telegram.ext import Dispatcher, Updater

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

WEBHOOK = bool(environ.get("WEBHOOK", False))
URL = environ.get("URL", "")  # Does not contain token
API_URL = environ.get("API_URL", "")  # No trailing slash
PORT = int(environ.get("PORT", 5000))
SUDO_USERS.add(OWNER_ID)
SUDO_USERS.update(get_users(sudo_users), SUDO_GROUPS)
TAG_USERS = get_users(tag_users)

UPDATER: Updater = Updater(token=TOKEN)
DISPATCHER: Dispatcher = UPDATER.dispatcher
roles: Roles = setup_roles(DISPATCHER)
roles.add_admin(OWNER_ID)

if "TAG_USERS" not in roles:
    roles.add_role("TAG_USERS")

if "SUDO_USERS" not in roles:
    roles.add_role("SUDO_USERS")

SUDO_USERS = roles["SUDO_USERS"]
TAG_USERS = roles["TAG_USERS"]
SUDO_USERS.add_child_role(TAG_USERS)
ADMINS = roles.admins

for sudo in get_users(sudo_users):
    SUDO_USERS.add_member(sudo)

for tag in get_users(tag_users):
    TAG_USERS.add_member(tag)
