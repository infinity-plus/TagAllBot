import requests
from ptbcontrib.reply_to_message_filter import ReplyToMessageFilter
from ptbcontrib.roles import RolesHandler
from telegram import Chat, Message, Update, User
from telegram.constants import CHAT_PRIVATE, PARSEMODE_MARKDOWN
from telegram.ext import CallbackContext, Filters, Job, JobQueue, PrefixHandler
from telegram.utils.helpers import mention_markdown

from tagall_bot import (
    ADMINS,
    API_URL,
    DISPATCHER,
    DND_USERS,
    LOGGER,
    PORT,
    SUDO_USERS,
    TAG_USERS,
    TOKEN,
    UPDATER,
    URL,
    WEBHOOK,
)
from tagall_bot.sql.roles import (
    add_sudo,
    add_tag,
    is_tag_user,
    remove_sudo,
    remove_tag,
)
from tagall_bot.texts import BAD_TEXT, HELP_TEXT, START_TEXT


def start(update: Update, _: CallbackContext) -> None:
    if isinstance(update.effective_message, Message):
        update.effective_message.reply_text(
            text=START_TEXT,
            parse_mode=PARSEMODE_MARKDOWN,
        )


def help(update: Update, _: CallbackContext) -> None:
    if isinstance(update.effective_message, Message):
        update.effective_message.reply_text(
            text=HELP_TEXT,
            parse_mode=PARSEMODE_MARKDOWN,
        )


def send_tag(context: CallbackContext) -> None:
    if isinstance(context.job, Job):
        context.bot.send_message(
            text=", ".join(context.job.context[2]),
            chat_id=context.job.context[0],
            reply_to_message_id=context.job.context[1],
            parse_mode=PARSEMODE_MARKDOWN,
        )


def mention_list(chat_id: int):
    r = requests.get(f"{API_URL}/get/{chat_id}")
    users = r.json() if r.status_code == 200 else {}
    return [
        mention_markdown(user_id, user_name)
        for user_id, user_name in users.items()
        if user_id not in DND_USERS
    ]


def split_list(array: list[str], chunk_size: int):
    """
    Splits a given list evenly into chunk_size.
    https://stackoverflow.com/a/312464/9664447
    """
    for i in range(0, len(array), chunk_size):
        yield array[i : i + chunk_size]


def schedule_job(
    context: CallbackContext,
    chat_id: int,
    message_id: int,
    tag: list[str],
    delay: int,
):
    if isinstance(context.job_queue, JobQueue):
        context.job_queue.run_once(
            callback=send_tag,
            when=3 * delay,
            context=(chat_id, message_id, tag),
        )


def tag_all(update: Update, context: CallbackContext) -> None:
    if (
        isinstance(update.effective_chat, Chat)
        and isinstance(update.effective_message, Message)
        and isinstance(update.effective_user, User)
    ):
        user = update.effective_user
        chat = update.effective_chat
        if user.id in TAG_USERS.chat_ids and not is_tag_user(user.id, chat.id):
            update.effective_message.reply_text(
                text=f"Couldn't grant tag power to add *{user.full_name}*",
                parse_mode=PARSEMODE_MARKDOWN,
            )
        message_id = update.effective_message.reply_to_message.message_id
        tags = mention_list(update.effective_chat.id)
        for i, tag in enumerate(split_list(list(tags), 5)):
            schedule_job(context, update.effective_chat.id, message_id, tag, i)


def bad_tag(update: Update, _: CallbackContext) -> None:
    if isinstance(update.effective_message, Message) and isinstance(
        update.effective_chat, Chat
    ):
        if update.effective_chat.type == CHAT_PRIVATE:
            update.effective_message.reply_text(
                text=BAD_TEXT[0],
                parse_mode=PARSEMODE_MARKDOWN,
            )
        elif update.effective_message.reply_to_message is None:
            update.effective_message.reply_text(
                text="Please reply to a message to tag all users of the chat.",
                parse_mode=PARSEMODE_MARKDOWN,
            )
        else:
            update.effective_message.reply_text(
                text=BAD_TEXT[1],
                parse_mode=PARSEMODE_MARKDOWN,
            )


def add_tag_user(update: Update, _: CallbackContext):
    if isinstance(update.effective_message, Message) and isinstance(
        update.effective_chat, Chat
    ):
        user: User = update.effective_message.reply_to_message.from_user
        if add_tag(
            user.id,
            update.effective_chat.id,
        ):
            TAG_USERS.add_member(user.id)
            update.effective_message.reply_text(
                text=f"Granted *tag* power to *{user.full_name}*",
                parse_mode=PARSEMODE_MARKDOWN,
            )
        else:
            update.effective_message.reply_text(
                text=f"Couldn't grant tag power to add *{user.full_name}*",
                parse_mode=PARSEMODE_MARKDOWN,
            )


def add_sudo_user(update: Update, _: CallbackContext):
    if isinstance(update.effective_message, Message):
        user: User = update.effective_message.reply_to_message.from_user
        if add_sudo(user.id):
            SUDO_USERS.add_member(user.id)
            update.effective_message.reply_text(
                text=f"Granted *superuser* power to *{user.full_name}*",
                parse_mode=PARSEMODE_MARKDOWN,
            )
        else:
            update.effective_message.reply_text(
                text=f"Couldn't grant superuser power to *{user.full_name}*",
                parse_mode=PARSEMODE_MARKDOWN,
            )


def bad_add(update: Update, _: CallbackContext) -> None:
    if isinstance(update.effective_message, Message) and isinstance(
        update.effective_chat, Chat
    ):
        if update.effective_chat.type == CHAT_PRIVATE:
            update.effective_message.reply_text(
                text=BAD_TEXT[0],
            )
        elif update.effective_message.reply_to_message is None:
            update.effective_message.reply_text(
                text="Please reply to a user to grant power.",
                parse_mode=PARSEMODE_MARKDOWN,
            )
        else:
            update.effective_message.reply_text(
                text=BAD_TEXT[1],
                parse_mode=PARSEMODE_MARKDOWN,
            )


def remove_tag_user(update: Update, _: CallbackContext):
    if isinstance(update.effective_message, Message):
        user: User = update.effective_message.reply_to_message.from_user
        if remove_tag(
            user.id,
            update.effective_message.chat.id,
        ):
            TAG_USERS.kick_member(user.id)
            update.effective_message.reply_text(
                text=f"Revoked *tag* power from *{user.full_name}*",
                parse_mode=PARSEMODE_MARKDOWN,
            )
        else:
            update.effective_message.reply_text(
                text=f"Couldn't revoked tag power from add *{user.full_name}*",
                parse_mode=PARSEMODE_MARKDOWN,
            )


def remove_sudo_user(update: Update, _: CallbackContext):
    if isinstance(update.effective_message, Message):
        user: User = update.effective_message.reply_to_message.from_user
        if remove_sudo(user.id):
            SUDO_USERS.kick_member(user.id)
            update.effective_message.reply_text(
                text=f"Revoked *superuser* power from *{user.full_name}*",
                parse_mode=PARSEMODE_MARKDOWN,
            )
        else:
            update.effective_message.reply_text(
                text=f"Couldn't revoke superuser power for *{user.full_name}*",
                parse_mode=PARSEMODE_MARKDOWN,
            )


def bad_remove(update: Update, _: CallbackContext) -> None:
    if isinstance(update.effective_message, Message) and isinstance(
        update.effective_chat, Chat
    ):
        if update.effective_chat.type == CHAT_PRIVATE:
            update.effective_message.reply_text(
                text=BAD_TEXT[0],
            )
        elif update.effective_message.reply_to_message is None:
            update.effective_message.reply_text(
                text="Please reply to a user to revoke power.",
                parse_mode=PARSEMODE_MARKDOWN,
            )
        else:
            update.effective_message.reply_text(
                text=BAD_TEXT[1],
                parse_mode=PARSEMODE_MARKDOWN,
            )


if __name__ == "__main__":
    LOGGER.info("Starting Tagall Bot...")
    LOGGER.info("Adding Handlers...")
    DISPATCHER.add_handler(
        PrefixHandler(
            prefix="!",
            command="start",
            callback=start,
        )
    )
    DISPATCHER.add_handler(
        PrefixHandler(
            prefix="!",
            command="help",
            callback=help,
        )
    )
    DISPATCHER.add_handler(
        RolesHandler(
            PrefixHandler(
                prefix=["!", "@"],
                command=["tag", "everyone"],
                callback=tag_all,
                filters=ReplyToMessageFilter(filters=Filters.all),
                run_async=True,
            ),
            roles=TAG_USERS,
        )
    )
    DISPATCHER.add_handler(
        PrefixHandler(
            prefix=["!", "@"],
            command=["tag", "everyone"],
            callback=bad_tag,
            run_async=True,
        )
    )
    DISPATCHER.add_handler(
        RolesHandler(
            PrefixHandler(
                prefix="!",
                command="grant",
                callback=add_tag_user,
                filters=Filters.chat_type.groups,
                run_async=True,
            ),
            roles=SUDO_USERS,
        )
    )
    DISPATCHER.add_handler(
        RolesHandler(
            PrefixHandler(
                prefix="!",
                command="grant_su",
                callback=add_sudo_user,
                filters=Filters.chat_type.groups,
                run_async=True,
            ),
            roles=ADMINS,
        )
    )
    DISPATCHER.add_handler(
        PrefixHandler(
            prefix="!",
            command=["grant", "grant_su"],
            callback=bad_add,
        )
    )
    DISPATCHER.add_handler(
        RolesHandler(
            PrefixHandler(
                prefix="!",
                command="revoke",
                callback=remove_tag_user,
                filters=Filters.chat_type.groups,
                run_async=True,
            ),
            roles=SUDO_USERS,
        )
    )
    DISPATCHER.add_handler(
        RolesHandler(
            PrefixHandler(
                prefix="!",
                command="revoke_su",
                callback=remove_sudo_user,
                filters=Filters.chat_type.groups,
                run_async=True,
            ),
            roles=ADMINS,
        )
    )
    DISPATCHER.add_handler(
        PrefixHandler(
            prefix="!",
            command=["revoke", "revoke_su"],
            callback=bad_remove,
        )
    )
    if WEBHOOK:
        LOGGER.info("Using Webhook...")
        UPDATER.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=URL + TOKEN,
        )
    else:
        LOGGER.info("Using Long Polling...")
        UPDATER.start_polling()
    UPDATER.idle()
