"""The module for constant text strings used throughout the project."""
START_TEXT = """
Hi! I'm **Tagall Bot**.

I'm a bot that tags all the users in a group.
You can use me to tag users in a group."""

HELP_TEXT = """
Reply to any message with one of the following:
`@everyone`
`!everyone`
`@tag`
`!tag`
and, shall tag everyone to that message."""

BAD_TEXT = (
    "You can't use this command in private chats.",
    "You are not allowed to use this command.",
)

ERROR_TEXT = {
    "MultipleResultsFound": "Multiple Tag Users with user_id={}; chat_id={}",
}

SEPARATOR = "---------------------------------------------------------------\n"
