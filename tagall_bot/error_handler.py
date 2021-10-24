import html
import io
import random
import sys
import traceback
from string import ascii_uppercase

import pretty_errors
import requests
from tagall_bot import OWNER_ID
from tagall_bot.texts import SEPARATOR
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
    User,
)
from telegram.ext import CallbackContext

pretty_errors.mono()


class ErrorsDict(dict):
    "A custom dict to store errors and their count"

    def __init__(self, *args, **kwargs):
        self.raw = []
        super().__init__(*args, **kwargs)

    def __contains__(self, error):
        self.raw.append(error)
        error.identifier = "".join(random.choices(ascii_uppercase, k=5))
        for e in self:
            if type(e) is type(error) and e.args == error.args:
                self[e] += 1
                return True
        self[error] = 0
        return False

    def __len__(self):
        return len(self.raw)


errors = ErrorsDict()


def error_callback(update: Update, context: CallbackContext):
    if not update:
        return
    if context.error in errors:
        return
    try:
        stringio = io.StringIO()
        pretty_errors.output_stderr = stringio
        pretty_errors.output_stderr = sys.stderr
        pretty_error = stringio.getvalue()
        stringio.close()
    except:  # noqa
        pretty_error = "Failed to create pretty error."
    if not isinstance(context.error, Exception):
        return
    tb_list = traceback.format_exception(
        None,
        context.error,
        context.error.__traceback__,
    )
    tb = "".join(tb_list)
    if not isinstance(update.effective_user, User):
        return
    pretty_message = (
        "{}\n"
        f"{SEPARATOR}"
        "An exception was raised while handling an update\n"
        "User: {}\n"
        "Chat: {} {}\n"
        "Callback data: {}\n"
        "Message: {}\n\n"
        "Full Traceback: {}"
    ).format(
        pretty_error,
        update.effective_user.id,
        update.effective_chat.title if update.effective_chat else "",
        update.effective_chat.id if update.effective_chat else "",
        update.callback_query.data if update.callback_query else "None",
        update.effective_message.text if update.effective_message else "None",
        tb,
    )
    key = requests.post(
        "https://nekobin.com/api/documents",
        json={"content": pretty_message},
    ).json()
    e = html.escape(f"{context.error}")
    if not key.get("result", {}).get("key"):
        with open("error.txt", "w+") as f:
            f.write(pretty_message)
        context.bot.send_document(
            OWNER_ID,
            open("error.txt", "rb"),
            caption=f"#{context.error.identifier}\n"  # type: ignore
            + f"<b>An unknown error occured:</b>\n<code>{e}</code>",
            parse_mode="html",
        )
        return
    key = key.get("result").get("key")
    url = f"https://nekobin.com/{key}.py"
    context.bot.send_message(
        OWNER_ID,
        text=f"#{context.error.identifier}\n"  # type: ignore
        + f"<b>An unknown error occured:</b>\n<code>{e}</code>",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Error", url=url)]],
        ),
        parse_mode="html",
    )


def list_errors(update: Update, context: CallbackContext):
    if not isinstance(update.effective_user, User):
        return
    if update.effective_user.id != OWNER_ID:
        return
    e = {
        k: v
        for k, v in sorted(
            errors.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    }
    msg = "<b>Errors List:</b>\n"
    for x, value in e.items():
        msg += f"• <code>{x}:</code> <b>{value}</b> #{x.identifier}\n"
    msg += f"{len(errors)} have occurred since startup."
    if len(msg) > 4096:
        with open("errors_msg.txt", "w+") as f:
            f.write(msg)
        context.bot.send_document(
            update.effective_chat.id if update.effective_chat else OWNER_ID,
            open("errors_msg.txt", "rb"),
            caption="Too many errors have occured..",
            parse_mode="html",
        )
        return
    if not isinstance(update.effective_message, Message):
        return
    update.effective_message.reply_text(msg, parse_mode="html")
