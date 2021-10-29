from ptbcontrib.roles import Role, RolesHandler
from telegram.ext import PrefixHandler
from telegram.ext.filters import BaseFilter

from tagall_bot import DISPATCHER


def command_handler(
    commands: str | list[str],
    prefix: str | list[str],
    filters: BaseFilter | None = None,
    run_async: bool = False,
    roles: Role | None = None,
):
    """A decorator to register the callback to dispatcher.
    Args:
        commands (str | list[str]): The command(s) to register.
        prefix (str | list[str]): The prefix(es) to register.
        filters (BaseFilter | None): The filter(s) to register.
        run_async (bool): Whether the callback should be run asynchronously.
        roles (Role | None): The role(s) to register.
    """

    def decorator(func):
        handler = PrefixHandler(
            prefix=prefix,
            command=commands,
            callback=func,
            filters=filters,
            run_async=run_async,
        )
        if roles is not None:
            handler = RolesHandler(handler=handler, roles=roles)
        DISPATCHER.add_handler(handler)
        return func

    return decorator
