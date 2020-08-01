from typing import TYPE_CHECKING

import asyncio
from pynput.mouse import Button

if TYPE_CHECKING:
    from .manager import Manager

from pynput import keyboard, mouse


class MouseListener:
    def __init__(self, manager: "Manager"):
        self.manager = manager
        self.listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)

    def start(self):
        self.listener.start()

    def on_move(self, x: int, y: int):
        # TODO Redirect input to manager
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
        # TODO Redirect input to manager
        pass

    def on_scroll(self, x: int, y: int, dx: int, dy: int):
        """
        dy is positive when scrolling up
        dy is negative when scrolling down
        """
        # TODO Redirect input to manager
        pass


if __name__ == "__main__":
    # Local testing

    async def main():
        listener = MouseListener(None)
        listener.start()

    asyncio.run(main())
