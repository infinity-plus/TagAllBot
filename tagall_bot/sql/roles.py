import threading

from sqlalchemy import Column, BigInteger, Integer

from tagall_bot.sql import BASE, SESSION


class sudo_users(BASE):
    __tablename__ = "sudo_users"
    user_id = Column(BigInteger, primary_key=True)

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return f"<Sudo user {self.user_id}>"


class tag_users(BASE):
    __tablename__ = "tag_users"
    pk = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    chat_id = Column(BigInteger)

    def __init__(self, user_id: int | str, chat_id: int | str):
        self.user_id = int(user_id)
        self.chat_id = int(chat_id)

    def __repr__(self):
        return f"<Tag user {self.user_id} of {self.chat_id}>"


sudo_users.__table__.create(checkfirst=True)
tag_users.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def get_users(table: sudo_users | tag_users) -> set[int]:
    try:
        all_users = SESSION.query(table.user_id)
    finally:
        SESSION.close()
    return {int(user.user_id[0]) for user in all_users}


def is_tag_user(user_id: int, chat_id: int) -> bool:
    try:
        user = SESSION.query(tag_users).get((user_id, chat_id))
    finally:
        SESSION.close()
    return bool(user)


def add_sudo(user_id: int):
    with INSERTION_LOCK:
        user = SESSION.query(sudo_users).get(user_id)
        if user is None:
            SESSION.add(sudo_users(user_id))
            SESSION.commit()
            return True
        return False


def add_tag(user_id: int, chat_id: int):
    with INSERTION_LOCK:
        user = SESSION.query(tag_users).get((user_id, chat_id))
        if not user:
            SESSION.add(tag_users(user_id, chat_id))
            SESSION.commit()
            return True
        return False


def remove_sudo(user_id: int):
    with INSERTION_LOCK:
        user = SESSION.query(sudo_users).get(user_id)
        if user:
            SESSION.delete(user)
            SESSION.commit()
            return True
        return False


def remove_tag(user_id: int, chat_id: int):
    with INSERTION_LOCK:
        user = SESSION.query(tag_users).get((user_id, chat_id))
        if user:
            SESSION.delete(user)
            SESSION.commit()
            return True
        return False
