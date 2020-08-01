import enum
import time
from dataclasses import dataclass, field
from typing import Optional, List, Generator, Union


class InputMode(enum.Enum):
    # The condition when the action should be triggered
    Undefined = 0
    OnPressed = 1
    OnReleased = 2


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
    click: Click
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
    # Which key to press
    key: str
    # Which modifiers to hold down when pressing the key
    ctrl: bool = None
    alt: bool = None
    shift: bool = None
    # When pressing hotkeys: delay between keyboard actions
    delay: int = 0
    # When holding down a key: duration how long a key will be held down
    duration: int = 0

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


@dataclass
class KeyboardAction:
    # The text to write
    text: str = ""
    # Between each character, have this amount of milliseconds delay
    character_delay: int = 0
    # Before executing this action, how much delay should there be
    start_delay: int = 0

    def next(self) -> Generator[Union[int, KeyInfo], None, None]:
        """
        This function returns the instruction to the thread:
        yield an integer which means waiting time in milliseconds
        yield a KeyInfo which means that keypress should be executed
        (in MouseAction: yield a MouseInfo which means that mouse action should be executed)
        """
        if self.start_delay:
            yield self.start_delay
        # TODO
        """
        What kind of actions should be allowed?
        
        write text (with modifiers, ctrl alt shift): abcd with start delay and character delay, if toggled: repeat text?
        pyautogui.hotkey('ctrl', 'c')
        
        hold down a key for X seconds and another key for Y seconds
        
        """


@dataclass
class MouseAction:
    # The text to write
    click: Click = Click.Left
    # Coordinates where to click, set to 'None' if mouse should not move
    coordinate_x: Optional[int] = None
    coordinate_y: Optional[int] = None
    # Coordinaates where to click relative from current position
    relative_x: Optional[int] = None
    relative_y: Optional[int] = None

    # Before executing this action, how much delay should there be
    start_delay: int = 0


@dataclass
class Command:
    # CONDITIONS

    # Condition for modifiers: None if doesnt matter, True if modifier has to be active, False if modifier has to be not held down
    condition_ctrl: Optional[bool] = None
    condition_alt: Optional[bool] = None
    condition_shift: Optional[bool] = None

    # Which key to listen to
    condition_key: Optional[str] = None
    # 0 = on_pressed, 1 = keyboard_on_release
    condition_keyboard_mode: InputMode = InputMode.OnPressed

    # Which mouse click to listen to
    condition_mouse: Optional[Click] = None
    # 0 = on_pressed, 1 = keyboard_on_release
    condition_mouse_mode: InputMode = InputMode.OnPressed

    # OPTIONS

    # TODO Should this action be active until toggled off again?
    # option_toggle: bool = False

    # How long it should wait before the action should be started
    option_start_delay: int = 0
    # Once it has been executed the first time, whats the delay (in ms) for the next execution?
    option_repeat_delay: int = 10
    # How often will it be repeated? Will be ignored if option_toggle is set to 'True'
    option_repeat_count: int = 1

    # EXECUTION

    # Modifiers that should be used when the action is executed
    execute_use_ctrl: Optional[bool] = None
    exucte_use_alt: Optional[bool] = None
    exucte_use_shift: Optional[bool] = None


@dataclass
class KeyboardCommand(Command):
    execute_actions: List[KeyboardAction] = field(default_factory=lambda: [])


@dataclass
class MouseCommand(Command):
    execute_actions: List[MouseAction] = field(default_factory=lambda: [])
