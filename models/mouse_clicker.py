from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from .manager import Manager

from models.other import MouseInfo, Click, Command, Action
import pyautogui
import asyncio
from loguru import logger


class MouseClicker:
    def __init__(self, manager: "Manager"):
        self.manager = manager

    async def _left_click(self, x: Optional[int], y: Optional[int]):
        pyautogui.click(x, y)

    async def _right_click(self, x: Optional[int], y: Optional[int]):
        pyautogui.rightClick(x, y)

    async def _middle_click(self, x: Optional[int], y: Optional[int]):
        pyautogui.middleClick(x, y)

    # TODO Back and forward mouse buttons
    # TODO Hold down mouse button

    async def _double_click(self, x: Optional[int], y: Optional[int]):
        pyautogui.doubleClick(x, y)

    async def _move(self, x: int, y: int, duration_milliseconds: int):
        logger.info(f"Moving mouse to x={x} y={y} over duration {duration_milliseconds}")
        pyautogui.moveTo(x, y, duration=duration_milliseconds / 1000)

    async def do_mouse_action(self, mouse_info: MouseInfo):
        """ Do one mouse action """
        with self.manager.lock:
            if mouse_info.click == Click.Move:
                await self._move(mouse_info.x, mouse_info.y, mouse_info.duration)
            elif mouse_info.click == Click.DoubleClick:
                await self._double_click(mouse_info.x, mouse_info.y)
            elif mouse_info.click == Click.Left:
                await self._left_click(mouse_info.x, mouse_info.y)
            elif mouse_info.click == Click.Right:
                await self._right_click(mouse_info.x, mouse_info.y)
            elif mouse_info.click == Click.Middle:
                await self._middle_click(mouse_info.x, mouse_info.y)

    async def do_mouse_actions(self, mouse_infos: List[MouseInfo]):
        """ Do a sequence of mouse action: click, move, double click, right click """
        for mouse_info in mouse_infos:
            await self.do_mouse_action(mouse_info)
            await asyncio.sleep(mouse_info.delay / 1000)


@dataclass
class MouseAction(Action):
    # Coordinates where to click, set to 'None' if mouse should not move
    coordinate_x: Optional[int] = None
    coordinate_y: Optional[int] = None
    # Coordinaates where to click relative from current position
    relative_x: Optional[int] = None
    relative_y: Optional[int] = None

    def __post_init__(self):
        assert self.mouse_actions, f"Action field is empty"
        # TODO Only one field needs to be used: coordinate or relative or none of them


@dataclass
class MouseCommand(Command):
    mouse_action: MouseAction = None

    def __post_init__(self):
        assert isinstance(self.mouse_action, MouseAction)


if __name__ == "__main__":
    # Local testing

    async def main():
        clicker = MouseClicker(None)

        # Double click, then rightclick
        double_click = MouseInfo(click=Click.DoubleClick, delay=2000)
        right_click = MouseInfo(click=Click.Right)
        await clicker.do_mouse_actions([double_click, right_click])

    asyncio.run(main())
