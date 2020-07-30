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
logger.remove()
# Log to console
logger.add(sys.stdout, level="INFO")
# Log to file, max size 1 mb
logger.add("main.log", rotation="1 MB", level="INFO")

# Type annotation / hints
from typing import List, Iterable, Union, Set, Optional

from models.manager import Manager
from models.other import KeyInfo, Command, KeyboardCommand, MouseCommand, MouseAction, KeyboardAction


async def main():
    manager = Manager()

    # Examples

    # Add a command which listens to keyboard press combination 'alt+f', wait 1 second, press left click 5 times (with delay of 5ms)
    manager.add_command(
        MouseCommand(
            condition_alt=True,
            condition_key="f",
            option_start_delay=1000,
            option_repeat_delay=5,
            option_repeat_count=10,
            execute_actions=[MouseAction()],
        )
    )

    logger.info(f"Hotkey manager started")
    await manager.run()


if __name__ == "__main__":
    asyncio.run(main())
