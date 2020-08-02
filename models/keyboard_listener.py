import asyncio
from typing import TYPE_CHECKING

from pynput import keyboard
from pynput.keyboard import KeyCode

if TYPE_CHECKING:
    from .manager import Manager

from models.other import KeyInfo, MODIFIERS


class KeyboardListener:
    def __init__(self, manager: "Manager"):
        self.manager = manager
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.modifiers = KeyInfo("", False, False, False)

    def start(self):
        self.listener.start()

    def on_press(self, key: KeyCode):
        """
        key.char: str
        key.combining: None
        key.is_dead: bool
        key.vk: int

        if it was a modifier (ctrl, alt, shift):
        key.name: str
        key.value: KeyCode
        """
        if hasattr(key, "char"):
            self.manager.keyboard_on_press(
                KeyInfo(ctrl=self.modifiers.ctrl, alt=self.modifiers.alt, shift=self.modifiers.shift, key=key.char,)
            )
        elif hasattr(key, "name"):
            # Handle modifier keys
            if key.name == "ctrl":
                self.modifiers.ctrl = True
            elif key.name == "alt":
                self.modifiers.alt = True
            elif key.name == "shift":
                self.modifiers.shift = True
            if key.name in MODIFIERS:
                return
            # Just pressing a modifier (ctrl, alt or shift) does not trigger a hotkey
            self.manager.keyboard_on_press(
                KeyInfo(ctrl=self.modifiers.ctrl, alt=self.modifiers.alt, shift=self.modifiers.shift, key=key.name,)
            )

    def on_release(self, key: KeyCode):
        if hasattr(key, "char"):
            pass
        elif hasattr(key, "name"):
            # Handle modifier keys
            if key.name == "ctrl":
                self.modifiers.ctrl = False
            elif key.name == "alt":
                self.modifiers.alt = False
            elif key.name == "shift":
                self.modifiers.shift = False


if __name__ == "__main__":
    # Local testing
    class FakeManager:
        def keyboard_on_press(self, _):
            return

        def keyboard_on_release(self, _):
            return

    async def main():
        listener = KeyboardListener(FakeManager())
        listener.start()
        while 1:
            await asyncio.sleep(1)

    asyncio.run(main())
