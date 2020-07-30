import asyncio
from typing import List

from models.keyboard_listener import KeyboardListener
from models.keyboard_presser import KeyboardPresser
from models.mouse_clicker import MouseClicker
from models.mouse_listener import MouseListener
from models.other import KeyInfo, Command, KeyboardCommand, MouseCommand

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

        self.keyboard_commands: List[KeyboardCommand] = []
        self.mouse_commands: List[MouseCommand] = []

        self.mouse_listener.start()
        self.keyboard_listener.start()

    async def run(self):
        while 1:
            # TODO Exit when special button has been pressed
            await asyncio.sleep(1)

    def add_command(self, command: Command):
        # TODO
        pass

    def on_press(self, key: KeyInfo):
        # TODO
        pass

    def on_release(self, key: KeyInfo):
        # TODO
        pass
