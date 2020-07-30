from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import Manager


class KeyboardPresser:
    def __init__(self, manager: "Manager"):
        self.manager = manager
