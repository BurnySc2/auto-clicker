import asyncio
from threading import Lock
from typing import List, Dict, Union
from collections import deque

from loguru import logger

from models.keyboard_listener import KeyboardListener
from models.keyboard_presser import KeyboardPresser
from models.mouse_clicker import MouseClicker
from models.mouse_listener import MouseListener
from models.other import KeyInfo, Command, KeyboardCommand, MouseCommand, InputMode

"""
Need to be able to apply commands like:
on alt = 9 -> left click 90 times after some seconds delay with click-repeat-delay of X milliseconds
"""


class Manager:
    def __init__(self):
        self.mouse_clicker = MouseClicker(self)
        self.mouse_listener = MouseListener(self)
        self.keyboard_presser = KeyboardPresser(self)
        self.keyboard_listener = KeyboardListener(self)

        self.keyboard_commands: Dict[str, List[KeyboardCommand]] = {}
        self.mouse_commands: Dict[int, List[MouseCommand]] = {}
        self.lock = Lock()
        self.queued_commands = deque()

        self.mouse_listener.start()
        self.keyboard_listener.start()


    async def run(self):
        while 1:
            # TODO Exit when special button has been pressed
            await asyncio.sleep(1)

    def add_command(self, command: Union[KeyboardCommand, MouseCommand]):
        assert isinstance(command, (KeyboardCommand, MouseCommand)), f"{type(command)}"

        if isinstance(command, KeyboardCommand):

            pass
        elif isinstance(command, MouseCommand):
            pass
        # TODO
        pass

    def keyboard_on_press(self, key: KeyInfo):
        logger.info(f"Key pressed: {key}")
        commands = self.keyboard_commands.get(key.key.lower(), [])
        if not commands:
            return

        def condition_function(command: KeyboardCommand, key_info: KeyInfo):
            return (
                command.condition_keyboard_mode == InputMode.OnPressed
                and (command.condition_ctrl is None or command.condition_ctrl is key_info.ctrl)
                and (command.condition_alt is None or command.condition_alt is key_info.alt)
                and (command.condition_shift is None or command.condition_shift is key_info.shift)
            )

        with self.lock:
            for command in commands:
                if not condition_function(command, key):
                    continue

                # TODO Execute/Queue action
                """
                Either queue actions one by one - doesnt work for toggleable actions
                
                Or queue a new instance of a class
                that object has a 'next()' and 'on_end()' function i guess
                """

            pass
        # TODO
        pass

    def keyboard_on_release(self, key: KeyInfo):
        logger.info(f"Key released: {key}")
        with self.lock:
            pass
        # TODO
        pass
