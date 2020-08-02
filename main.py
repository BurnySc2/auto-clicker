# Other
import time
import os
import sys
import re
import time
import json
from contextlib import contextmanager
from pathlib import Path
from dataclasses import dataclass

# https://pypi.org/project/dataclasses-json/#description
from dataclasses_json import DataClassJsonMixin

# Coroutines and multiprocessing
import asyncio
import aiohttp
from multiprocessing import Process, Lock, Pool

# Simple logging https://github.com/Delgan/loguru
from loguru import logger

# Database
import sqlite3

# Remove previous default handlers
from models.keyboard_presser import KeyboardAction, KeyboardCommand
from models.mouse_clicker import MouseCommand, MouseAction

logger.remove()
# Log to console
logger.add(sys.stdout, level="INFO")
# Log to file, max size 1 mb
logger.add("main.log", rotation="1 MB", level="INFO")

# Type annotation / hints
from typing import List, Iterable, Union, Set, Optional

from models.manager import Manager
from models.other import KeyInfo, Command, ScriptCommand, MouseInfo, Click


async def main():
    manager = Manager()

    # Examples

    # Add a command which listens to keyboard press combination 'alt+f', wait 1 second, press left click 5 times (with delay of 5ms)
    # manager.add_hotkey(
    #     "alt+1", MouseCommand(start_delay=1000, repeat_delay=5, repeat_count=10, execute_actions=[MouseAction()],)
    # )

    # Hotkey "alt+1": Left click 3 times (initial click + 2 repeat clicks) which should select the whole line
    manager.add_hotkey(
        "alt+1",
        MouseCommand(
            mouse_action=MouseAction(
                manager, mouse_actions=[MouseInfo(click=Click.Left)], start_delay=1000, repeat_amount=2
            ),
        ),
    )

    # Hotkey: "hello": Write text " whats up buddy" with 1 second delay after you typed the word "hello"
    hotkey_text = "hello"
    manager.add_hotkey(
        ",".join(hotkey_text),
        KeyboardCommand(
            keyboard_action=KeyboardAction(
                manager, hotkeys_to_press=KeyInfo.from_text(" whats up buddy", key_delay=0), start_delay=1000
            ),
        ),
    )
    # Pressing escape will terminate this script
    # Can also be "async def my_exit()"
    def my_exit():
        logger.info(f"Ending program, escape was pressed!")
        manager.exit = True

    manager.add_hotkey(
        "esc", ScriptCommand(functions=[my_exit], start_delay=0),
    )

    logger.info(f"Hotkey manager started")
    await manager.run()


if __name__ == "__main__":
    asyncio.run(main())
