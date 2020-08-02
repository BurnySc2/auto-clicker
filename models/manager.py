import asyncio
import sys
from collections import deque
from threading import Thread, RLock
from typing import List, Union, Deque

from loguru import logger

from models.keyboard_listener import KeyboardListener
from models.keyboard_presser import KeyboardPresser, KeyboardCommand
from models.mouse_clicker import MouseClicker, MouseCommand
from models.other import KeyInfo, VALID_KEYS, KEYS_WITH_MODIFIERS, ScriptCommand

"""
Need to be able to apply commands like:
on alt = 9 -> left click 90 times after some seconds delay with click-repeat-delay of X milliseconds
"""


class Manager:
    def __init__(self):
        self.mouse_clicker = MouseClicker(self)
        self.keyboard_presser = KeyboardPresser(self)
        self.keyboard_listener = KeyboardListener(self)

        self.commands: List[Union[KeyboardCommand, MouseCommand, ScriptCommand]] = []
        self.lock = RLock()
        self.previously_pressed_hotkeys: Deque[KeyInfo] = deque()
        self.ignore_next_key_press: int = 0
        self.ignore_next_key_release: int = 0

        self.keyboard_listener.start()

        self.exit = False

    async def run(self):
        while 1:
            await asyncio.sleep(0.1)
            if self.exit:
                sys.exit(0)

    def parse_hotkey_combination(self, combination: str) -> List[KeyInfo]:
        key_infos = []
        for hotkey in combination.split(","):
            hotkey = hotkey.strip()
            keys = hotkey.split("+")
            key_info = KeyInfo("", False, False, False)
            for index, key in enumerate(keys):
                key = key.strip().lower()
                assert key in KEYS_WITH_MODIFIERS, f"A key from the hotkey has to be one of: {KEYS_WITH_MODIFIERS}"
                # Last key has to be a hotkey
                if index == len(keys) - 1:
                    assert key in VALID_KEYS, f"The final key of a hotkey has to be one of: {VALID_KEYS}"
                    key_info.key = key
                # Activate MODIFIERS
                elif key == "ctrl":
                    assert key_info.ctrl is False, f"Invalid hotkey: {hotkey}"
                    key_info.ctrl = True
                elif key == "alt":
                    assert key_info.alt is False, f"Invalid hotkey: {hotkey}"
                    key_info.alt = True
                elif key == "shift":
                    assert key_info.shift is False, f"Invalid hotkey: {hotkey}"
                    key_info.shift = True
            key_infos.append(key_info)
        assert key_infos, f"Could not find at least one hotkey from combination: {combination}"
        return key_infos

    def add_hotkey(self, hotkey_combination: str, command: Union[KeyboardCommand, MouseCommand, ScriptCommand]):
        assert isinstance(command, (KeyboardCommand, MouseCommand, ScriptCommand)), f"{type(command)}"
        # TODO Ignore case sensitivity
        hotkeys = self.parse_hotkey_combination(hotkey_combination)
        if len(hotkeys) == 1 or not all(hotkey == hotkeys[index + 1] for index, hotkey in enumerate(hotkeys[:-1])):
            logger.warning(
                f"Your hotkey combination is {hotkey_combination}. You proably do not want that unless you only want to trigger the hotkey once a specific amount of the same button has been pressed."
            )
        command.hotkeys = hotkeys

        self.commands.append(command)
        if isinstance(command, KeyboardCommand):
            logger.info(f"Adding hotkey combination {hotkeys} to execute keyboard actions {command.keyboard_action}")
        elif isinstance(command, MouseCommand):
            logger.info(f"Adding hotkey combination {hotkeys} to execute mouse actions {command.mouse_action}")
        elif isinstance(command, ScriptCommand):
            logger.info(f"Adding hotkey combination {hotkeys} to execute script {command.functions}")

    def keyboard_on_press(self, key_info: KeyInfo):
        # Ignore hotkeys pressed by this script
        if self.ignore_next_key_press > 0:
            self.ignore_next_key_press -= 1
            return

        logger.info(f"Key pressed: {key_info}")
        self.previously_pressed_hotkeys.appendleft(key_info)
        if len(self.previously_pressed_hotkeys) > 20:
            self.previously_pressed_hotkeys.pop()
        for command in self.commands:
            if command.pressed_keys_match_hotkey(self.previously_pressed_hotkeys):
                logger.info(f"Command was triggerend: {command}")
                # How to split asyncio here to execute in parallel? What if 2 hotkeys are pressed?
                # asyncio.create_task() doesnt work here because it runs on a seperate thread - no event loop runs on this thread
                if isinstance(command, ScriptCommand):
                    Thread(target=asyncio.run, args=[command.execute()]).start()
                elif isinstance(command, KeyboardCommand):
                    Thread(target=asyncio.run, args=[command.keyboard_action.execute()]).start()
                elif isinstance(command, MouseCommand):
                    Thread(target=asyncio.run, args=[command.mouse_action.execute()]).start()

    def keyboard_on_release(self, key_info: KeyInfo):
        if self.ignore_next_key_release > 0:
            self.ignore_next_key_release -= 1
            return
