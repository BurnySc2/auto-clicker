from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .manager import Manager

import pyautogui
import asyncio
from loguru import logger

from models.other import KeyInfo, Command, MODIFIERS, Action


class KeyboardPresser:
    def __init__(self, manager: "Manager"):
        self.manager = manager

    async def press_hotkey(self, key_info: KeyInfo, verbose=True):
        """ Presses a hotkey combination. """
        if verbose:
            logger.info(f"Pressing hotkey: {key_info.to_hotkey_list}")
        with self.manager.lock:
            pyautogui.hotkey(*key_info.to_hotkey_list)

    async def press_hotkeys(self, keys: List[KeyInfo]):
        """ Uses the function above to hit multilpe hotkeys while being able to sleep between action. """
        for index, key_info in enumerate(keys):
            logger.info(f"Pressing hotkey [{index+1} / {len(keys)}]: {key_info.to_hotkey_list}")
            await self.press_hotkey(key_info, verbose=False)
            await asyncio.sleep(key_info.delay / 1000)

    async def hold_down_button(self, key_info: KeyInfo):
        """ Hold down a button for X milliseconds. """
        key = key_info.key
        # Hold down MODIFIERS
        with self.manager.lock:
            for modifier_str, should_press in zip(MODIFIERS, [key_info.ctrl, key_info.alt, key_info.shift]):
                if should_press:
                    logger.info(f"Holding down modifier: {modifier_str}")
                    pyautogui.keyDown(f"{modifier_str}")

            # Hold down key
            self.manager.ignore_next_key_press += 1
            logger.info(f"Holding down button: {key_info.key}")
            pyautogui.keyDown(f"{key}")

        # Wait time
        await asyncio.sleep(key_info.duration / 1000)

        # Release key
        with self.manager.lock:
            logger.info(f"Releasing button: {key}")
            self.manager.ignore_next_key_release += 1
            pyautogui.keyUp(f"{key}")

            # Release MODIFIERS
            for modifier_str, should_release in zip(
                reversed(MODIFIERS), reversed([key_info.ctrl, key_info.alt, key_info.shift])
            ):
                if should_release:
                    logger.info(f"Releasing modifier: {key_info.key}")
                    pyautogui.keyDown(f"{modifier_str}")


@dataclass
class KeyboardAction(Action):
    def __post_init__(self):
        assert self.hotkeys_to_press, f"Action field is empty"


@dataclass
class KeyboardCommand(Command):
    keyboard_action: KeyboardAction = None

    def __post_init__(self):
        assert isinstance(self.keyboard_action, KeyboardAction)


if __name__ == "__main__":
    # Local testing

    async def main():
        presser = KeyboardPresser(None)

        key_info_ctrl_v = KeyInfo(key="v", ctrl=True)
        # Press hotkey (paste)
        # await presser.press_hotkey(key_info_ctrl_v)

        key_info_f = KeyInfo(key="F", delay=2000, duration=1000)
        key_info_s = KeyInfo(key="s", duration=500)
        # Press hotkey (f then s)
        await presser.press_hotkeys([key_info_f, key_info_s])

        # Hold down key for X seconds
        # await presser.hold_down_button(key_info_f)
        # await presser.hold_down_button(key_info_s)
        #
        # # Hold down multiple buttons
        # await asyncio.gather(presser.hold_down_button(key_info_f), presser.hold_down_button(key_info_s))

    asyncio.run(main())
