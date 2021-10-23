# Tag All Bot

A telegram bot that tags all the users in a group.

[![Python Version](https://img.shields.io/badge/python-3.10.0-blue.svg)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Usage:

Reply to any message with any one of the following:
* `@everyone`
* `!everyone`
* `@tag`
* `!tag`

And the bot shall tag everyone in that group.

Aditionally, **Bot owner** can use following commands:
* `!grant_su`: Grants the replied user with "superuser" role, i.e, they can use the bot in any chat.
* `!revoke_su`: Revokes the "superuser" role of the replied person.

**Bot owner** AND **Superusers** can use following commands:
* `!grant`: Grants the replied user with "tag" role, i.e, they can use the bot in that particular chat.
* `!revoke`: Revokes the "tag" role of the replied person.

## Deploying:

### Environment Variables:

#### Required

 - `TOKEN` : Bot token from [BotFather](https://t.me/Botfather).
 - `OWNER_ID` : Telegram user_id of owner. Get it via [@userinfobot](https://t.me/userinfobot).
 - `DATABASE_URL` : URL of your Postgres database. (Automatic if on Heroku).
 - `API_URL` : URL of the deployed chatidToMembersAPI. Deploy from here: [infinity-plus/chatToMembersAPI](https://github.com/infinity-plus/chatidToMembersAPI)

#### Optional

 - `WEBHOOK` : Set to any value to enable webhooks, otherwise, leave empty to disable webhooks.
 - `URL` : URL of server for webhooks. (Use `https://<appname>.herokuapp.com/` if on Heroku)
 - `SUDO_USERS` : Space separated list of user_ids that can use the bot everywhere.
 - `DND_USERS` : Space separated list of user_ids that will not be tagged by the bot.

### Deploying locally or on VPS:

* Clone the repo:

```
git clone https://github.com/YAIFoundation/TagAllBot.git
```

* Install the requirements:

```
cd TagAllBot
python3 -m pip install -r requirements.txt
```

* Start the Bot:

```
python3 -m tagall_bot
```

### Deploy on HEROKU

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Built with

* [Python 3.10.0](https://www.python.org/)
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot/)
* [Telethon](https://github.com/LonamiWebs/Telethon) (for `iter_participants`)

### Enhanced with:

* [ptbcontrib/roles](https://github.com/python-telegram-bot/ptbcontrib/tree/main/ptbcontrib/roles) (For roles management)
* [ptbcontrib/reply_to_message_filter](https://github.com/python-telegram-bot/ptbcontrib/tree/main/ptbcontrib/reply_to_message_filter) (For filters)
