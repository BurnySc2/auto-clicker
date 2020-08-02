# Other
# Coroutines and multiprocessing
import asyncio
import sys

# Simple logging https://github.com/Delgan/loguru
from loguru import logger

# Remove previous default handlers
from models.keyboard_presser import KeyboardAction, KeyboardCommand
from models.mouse_clicker import MouseCommand, MouseAction

logger.remove()
# Log to console
logger.add(sys.stdout, level="INFO")
# Log to file, max size 1 mb
logger.add("main.log", retention="10 days", level="INFO")

from models.manager import Manager
from models.other import KeyInfo, ScriptCommand, MouseInfo, Click


async def main():
    manager = Manager()

    # Examples

    # Hotkey "alt+1": Left click 3 times (initial click + 2 repeat clicks) which should select the whole line
    for i in range(1, 6):
        manager.add_hotkey(
            f"alt+{i}",
            MouseCommand(
                mouse_action=MouseAction(
                    manager,
                    mouse_actions=[MouseInfo(click=Click.Left)],
                    start_delay=1000,
                    repeat_amount=2 ** (2 + i) - 1,
                ),
            ),
        )

    # Hold down key F for 10 seconds
    manager.add_hotkey(
        "alt+f",
        KeyboardCommand(
            # TODO Simplify so that i dont hafve to pass 'manager' as parameter
            keyboard_action=KeyboardAction(manager, hotkeys_to_press=[KeyInfo("f", duration=10000)], start_delay=1000),
        ),
    )

    # Hold down key F for 30 seconds
    manager.add_hotkey(
        "alt+g",
        KeyboardCommand(
            # TODO Simplify so that i dont hafve to pass 'manager' as parameter
            keyboard_action=KeyboardAction(manager, hotkeys_to_press=[KeyInfo("f", duration=30000)], start_delay=1000),
        ),
    )

    # Press hotkey E 20 times
    manager.add_hotkey(
        "alt+e",
        KeyboardCommand(
            # TODO Simplify so that i dont hafve to pass 'manager' as parameter
            keyboard_action=KeyboardAction(
                manager, hotkeys_to_press=[KeyInfo("e")], start_delay=1000, repeat_amount=19
            ),
        ),
    )
    # Hotkey: "hello": Write text " whats up buddy" with 1 second delay after you typed the word "hello"
    # hotkey_text = "hello"
    # manager.add_hotkey(
    #     ",".join(hotkey_text),
    #     KeyboardCommand(
    #         # TODO Simplify so that i dont have to pass 'manager' as parameter
    #         keyboard_action=KeyboardAction(
    #             manager, hotkeys_to_press=KeyInfo.from_text(" whats up buddy", key_delay=0), start_delay=1000
    #         ),
    #     ),
    # )

    # Pressing escape will terminate this script
    # Can also be "async def my_exit()"
    def my_exit():
        logger.info(f"Ending program, escape was pressed!")
        manager.exit = True

    manager.add_hotkey(
        "alt+q", ScriptCommand(functions=[my_exit], start_delay=0),
    )

    logger.info(f"Hotkey manager started")
    await manager.run()


if __name__ == "__main__":
    asyncio.run(main())
