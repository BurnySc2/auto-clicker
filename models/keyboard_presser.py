from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .manager import Manager

import pyautogui
import asyncio
from loguru import logger

from models.other import KeyInfo

modifiers = ["ctrl", "alt", "shift"]


class KeyboardPresser:
    def __init__(self, manager: "Manager"):
        self.manager = manager

    async def press_hotkey(self, key_info: KeyInfo, verbose=True):
        """ Presses a hotkey combination. """
        if verbose:
            logger.info(f"Pressing hotkey: {key_info.to_hotkey_list}")
        pyautogui.hotkey(*key_info.to_hotkey_list)

    async def press_hotkeys(self, keys: List[KeyInfo]):
        """ Uses the function above to hit multilpe hotkeys while being able to sleep between actions. """
        for index, key_info in enumerate(keys):
            logger.info(f"Pressing hotkey [{index+1} / {len(keys)}]: {key_info.to_hotkey_list}")
            await self.press_hotkey(key_info, verbose=False)
            await asyncio.sleep(key_info.delay / 1000)

    async def hold_down_button(self, key_info: KeyInfo):
        """ Hold down a button for X milliseconds. """
        key = key_info.key.lower()
        # TODO if ctrl or alt or shift is true: press

        # Hold down modifiers
        for modifier_str, should_press in zip(modifiers, [key_info.ctrl, key_info.alt, key_info.shift]):
            if should_press:
                logger.info(f"Holding down modifier: {modifier_str}")
                pyautogui.keyDown(f"{modifier_str}")

        # Hold down key
        logger.info(f"Holding down button: {key_info.key}")
        pyautogui.keyDown(f"{key}")

        # Wait time
        await asyncio.sleep(key_info.duration / 1000)

        # Release key
        logger.info(f"Releasing button: {key}")
        pyautogui.keyUp(f"{key}")

        # Release modifiers
        for modifier_str, should_release in zip(
            reversed(modifiers), reversed([key_info.ctrl, key_info.alt, key_info.shift])
        ):
            if should_release:
                logger.info(f"Releasing modifier: {key_info.key}")
                pyautogui.keyDown(f"{modifier_str}")


if __name__ == "__main__":
    # Local testing

    async def main():
        presser = KeyboardPresser(None)

        key_info_ctrl_v = KeyInfo(key="v", ctrl=True)
        # Press hotkey (paste)
        await presser.press_hotkey(key_info_ctrl_v)

        key_info_f = KeyInfo(key="f", delay=2000, duration=1000)
        key_info_s = KeyInfo(key="s", duration=500)
        # Press hotkey (f then s)
        await presser.press_hotkeys([key_info_f, key_info_s])

        # Hold down key for X seconds
        await presser.hold_down_button(key_info_f)
        await presser.hold_down_button(key_info_s)

        # Hold down multiple buttons
        await asyncio.gather(presser.hold_down_button(key_info_f), presser.hold_down_button(key_info_s))

    asyncio.run(main())
