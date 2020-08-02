import asyncio
import enum
import string
from dataclasses import dataclass, field
from typing import Optional, List, Generator, Union, Deque, Awaitable, TYPE_CHECKING


if TYPE_CHECKING:
    from models.manager import Manager

VALID_KEYS = {"space", "esc"}
# Add numbers and lower case letters
for key in string.ascii_lowercase + string.digits:
    VALID_KEYS.add(key)
# Add f1 to f12
for number in range(1, 13):
    VALID_KEYS.add(f"f{number}")

MODIFIERS = ["ctrl", "alt", "shift"]
KEYS_WITH_MODIFIERS = VALID_KEYS | set(MODIFIERS)


class Click(enum.Enum):
    # What mouse action to do
    Undefined = 0
    Left = 1
    Right = 3
    Middle = 2
    Back = 8
    Forward = 9
    DoubleClick = 97
    Move = 98
    MoveRelative = 99


@dataclass
class MouseInfo:
    click: Click = Click.Left
    # Move to monitor coordinaate
    x: Optional[int] = None
    y: Optional[int] = None
    # Move relative to current location
    relative_x: Optional[int] = None
    relative_y: Optional[int] = None
    # Delay between mouse clicks
    delay: int = 0
    # How long a mouse moves to target location
    duration: int = 0


@dataclass
class KeyInfo:
    # Which key to press or was pressed
    key: str
    # Which MODIFIERS to hold down when pressing the key
    ctrl: bool = None
    alt: bool = None
    shift: bool = None
    # When pressing hotkeys: delay between keyboard action
    delay: int = 0
    # When holding down a key: duration how long a key will be held down
    duration: int = 0

    def __post_init__(self):
        assert len(key) > 0, f"Key needs to be at least of length 1: {self.key}"

    @classmethod
    def from_text(cls, text: str, key_delay: int = 0) -> List["KeyInfo"]:
        return [KeyInfo(key, delay=key_delay) for key in text]

    @property
    def to_hotkey_list(self) -> List[str]:
        keys = []
        if self.ctrl:
            keys.append("ctrl")
        if self.alt:
            keys.append("alt")
        if self.shift:
            keys.append("shift")
        keys.append(self.key)
        return keys

    def copy(self) -> "KeyInfo":
        return KeyInfo(self.key, self.ctrl, self.alt, self.shift, self.delay, self.duration)

    def __eq__(self, other: "KeyInfo"):
        assert isinstance(other, KeyInfo)
        return self.key == other.key and all(
            self_modifier is None or other_modifier is None or self_modifier is other_modifier
            for self_modifier, other_modifier in zip(
                [self.ctrl, self.alt, self.shift], [other.ctrl, other.alt, other.shift]
            )
        )

    def __ne__(self, other: "KeyInfo"):
        # TODO Is this needed or will __eq__ suffice? I assume dataclass will have its own __ne__ function so I will have override it
        return not (self == other)


@dataclass
class Action:
    manager: "Manager"

    # For mouse actions: where to click
    mouse_actions: List[MouseInfo] = field(default_factory=lambda: [])

    # For keyboard actions: hotkeys to press
    hotkeys_to_press: List[KeyInfo] = field(default_factory=lambda: [])

    # How long it should wait before the action should be started
    start_delay: int = 0
    # Once it has been executed the first time, whats the delay (in ms) for the next execution?
    repeat_delay: int = 10
    # How often will it be repeated? Will be ignored if option_toggle is set to 'True'
    repeat_amount: int = 0
    # TODO Toggle on / off
    toggled_state: bool = False

    def __post_init__(self):
        assert self.start_delay >= 0, f"{self.start_delay}"
        assert self.repeat_delay >= 0, f"{self.repeat_delay}"
        assert self.repeat_amount >= 0, f"{self.repeat_amount}"

    def actions(self) -> Generator[Union[int, Union[KeyInfo, MouseInfo]], None, None]:
        """
        This function returns the instruction to the thread:
        yield an integer which means waiting time in milliseconds
        yield a KeyInfo which means that keypress should be executed
        (in MouseAction: yield a MouseInfo which means that mouse action should be executed)
        """
        if self.start_delay:
            yield self.start_delay
        while 1:
            for _ in range(self.repeat_amount + 1):
                for key_info in self.hotkeys_to_press:
                    assert isinstance(key_info, KeyInfo)
                    yield key_info
                    yield key_info.delay
                for mouse_info in self.mouse_actions:
                    assert isinstance(mouse_info, MouseInfo)
                    yield mouse_info
                    yield mouse_info.delay
                yield self.repeat_delay
            if not self.toggled_state:
                return

    async def execute(self):
        for action in self.actions():
            if isinstance(action, int):
                await asyncio.sleep(action / 1000)
            elif isinstance(action, KeyInfo):
                # Press keyboard hotkey / combination
                if action.duration > 0:
                    await self.manager.keyboard_presser.hold_down_button(self.manager, action)
                else:
                    self.manager.ignore_next_key_press += 1
                    await self.manager.keyboard_presser.press_hotkey(self.manager, action)
            elif isinstance(action, MouseInfo):
                # Press mouse
                await self.manager.mouse_clicker.do_mouse_action(action)


@dataclass
class Command:
    # TRIGGER CONDITIONS
    hotkeys: List[KeyInfo] = field(default_factory=lambda: [])

    # Which mouse click to listen to
    condition_mouse: Optional[Click] = None

    # OPTIONS
    # TODO Should this action be active until toggled off again?
    # option_toggle: bool = False

    def __post_init__(self):
        assert not self.hotkeys, f"Do not enter data here. Will be filled out automatically by the script."

    def pressed_keys_match_hotkey(self, previous_hotkeys: Deque[KeyInfo]) -> bool:
        if len(self.hotkeys) > len(previous_hotkeys):
            return False
        for hotkey, previous_hotkey in zip(reversed(self.hotkeys), previous_hotkeys):
            if hotkey != previous_hotkey:
                return False
        return True


@dataclass
class ScriptCommand(Command):
    functions: List[Union[callable, Awaitable]] = field(default_factory=lambda: [])
    start_delay: int = 0

    def __post_init__(self):
        assert self.start_delay >= 0, f"{self.start_delay}"

    async def execute(self):
        if self.start_delay:
            await asyncio.sleep(self.start_delay / 1000)

        for execute_function in self.functions:
            # logger.info(f"Type iscallable: {callable(execute_function)}")
            # logger.info(f"Type isfuture: {asyncio.isfuture(execute_function)}")
            # logger.info(f"Type iscoroutine: {asyncio.iscoroutine(execute_function)}")
            # logger.info(f"Type iscoroutinefunction: {asyncio.iscoroutinefunction(execute_function)}")

            # # Is Async function
            if asyncio.iscoroutinefunction(execute_function):
                asyncio.create_task(execute_function())
                # await execute_function()
            # Is Async function but already was executed() but not awaited
            elif asyncio.iscoroutine(execute_function):
                asyncio.create_task(execute_function)
                # await execute_function
            # Is just a normal function waiting to be called
            elif callable(execute_function):
                execute_function()
