from typing import TYPE_CHECKING, Tuple, TypeVar, Union

_Key =  Union[str, int]  # typing for key inputs
_MouseButton = int  # Mousebutton typing
_MouseButtonStates = Tuple[_MouseButton, _MouseButton, _MouseButton]

if TYPE_CHECKING:
    from .actor import Actor

_ActorType = TypeVar("_ActorType", bound="Actor")
