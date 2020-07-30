from typing import TYPE_CHECKING

from pynput import keyboard, mouse
from pynput.keyboard import KeyCode

if TYPE_CHECKING:
    from .manager import Manager

from .other import KeyInfo


class KeyboardListener:
    def __init__(self, handler: "Manager"):
        self.handler = handler
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.modifiers = KeyInfo(False, False, False, "")

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
            self.handler.on_press(
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
            self.handler.on_press(
                KeyInfo(ctrl=self.modifiers.ctrl, alt=self.modifiers.alt, shift=self.modifiers.shift, key=key.name,)
            )

    def on_release(self, key: KeyCode):
        if hasattr(key, "char"):
            self.handler.on_release(
                KeyInfo(ctrl=self.modifiers.ctrl, alt=self.modifiers.alt, shift=self.modifiers.shift, key=key.char,)
            )
        elif hasattr(key, "name"):
            # Handle modifier keys
            if key.name == "ctrl":
                self.modifiers.ctrl = False
            elif key.name == "alt":
                self.modifiers.alt = False
            elif key.name == "shift":
                self.modifiers.shift = False
            self.handler.on_release(
                KeyInfo(ctrl=self.modifiers.ctrl, alt=self.modifiers.alt, shift=self.modifiers.shift, key=key.name,)
            )
