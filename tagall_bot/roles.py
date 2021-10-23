from enum import Enum

from ptbcontrib.roles import Role, Roles, setup_roles

from tagall_bot import DISPATCHER, OWNER_ID, SUDO_GROUPS, SUDO_USERS, TAG_USERS
from tagall_bot.sql.roles import (
    add_sudo_user,
    add_tag_user,
    remove_sudo_user,
    remove_tag_user,
)

roles: Roles = setup_roles(DISPATCHER)
roles.add_admin(OWNER_ID)

if "TAG_USERS" not in roles:
    roles.add_role("TAG_USERS", list(TAG_USERS))

if "SUDO_USERS" not in roles:
    roles.add_role(
        name="SUDO_USERS",
        chat_ids=(*SUDO_USERS, *SUDO_GROUPS),
        child_roles=roles["TAG_USERS"],
    )


class USERS(Enum):
    SUDO_USERS = "SUDO_USERS"
    TAG_USERS = "TAG_USERS"


def add_user_to_role(
    user_id: int,
    role: USERS,
    chat_id: int | None = None,
) -> bool:
    if role in roles:
        if role == USERS.SUDO_USERS:
            result = add_sudo_user(user_id)
        elif role == USERS.TAG_USERS and chat_id is not None:
            result = add_tag_user(user_id, chat_id)
        else:
            result = False
        if result:
            roles[role.value].add_member(user_id)
            return True
    return False


def remove_user_from_role(
    user_id: int,
    role: USERS,
    chat_id: int | None = None,
) -> bool:
    if role in roles:
        if role == USERS.SUDO_USERS:
            result = remove_sudo_user(user_id)
        elif role == USERS.TAG_USERS and chat_id is not None:
            result = remove_tag_user(user_id, chat_id)
        else:
            result = False
        if result:
            roles[role.value].kick_member(user_id)
            return True
    return False


for SUDO in SUDO_USERS:
    add_user_to_role(SUDO, USERS.SUDO_USERS)
SUDO_USERS: Role = roles["SUDO_USERS"]
TAG_USERS: Role = roles["TAG_USERS"]
ADMIN: Role = roles.admins
