from typing import TYPE_CHECKING

from pynput.mouse import Button

if TYPE_CHECKING:
    from .manager import Manager

from pynput import keyboard, mouse


class MouseListener:
    def __init__(self, handler: "Manager"):
        self.handler = handler
        self.listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)

    def start(self):
        self.listener.start()

    def on_move(self, x: int, y: int):
        pass

    def on_click(self, x: int, y: int, button: Button, pressed: bool):
        """
        button.button:
            left: 1
            middle: 2
            right: 3
            button8 = 8
            button9 = 9
        """
        pass

    def on_scroll(self, x: int, y: int, dx: int, dy: int):
        """
        dy is positive when scrolling up
        dy is negative when scrolling down
        """
        pass
