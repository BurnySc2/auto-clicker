from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import Manager


class MouseClicker:
    def __init__(self, handler: "Manager"):
        self.handler = handler
