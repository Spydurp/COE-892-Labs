from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class mapRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class mapReply(_message.Message):
    __slots__ = ("map", "bounds")
    MAP_FIELD_NUMBER: _ClassVar[int]
    BOUNDS_FIELD_NUMBER: _ClassVar[int]
    map: str
    bounds: str
    def __init__(self, map: _Optional[str] = ..., bounds: _Optional[str] = ...) -> None: ...

class cmdReq(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: int
    def __init__(self, size: _Optional[int] = ...) -> None: ...

class cmdReply(_message.Message):
    __slots__ = ("commands",)
    COMMANDS_FIELD_NUMBER: _ClassVar[int]
    commands: str
    def __init__(self, commands: _Optional[str] = ...) -> None: ...

class serialRequest(_message.Message):
    __slots__ = ("posX", "posY", "id")
    POSX_FIELD_NUMBER: _ClassVar[int]
    POSY_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    posX: int
    posY: int
    id: int
    def __init__(self, posX: _Optional[int] = ..., posY: _Optional[int] = ..., id: _Optional[int] = ...) -> None: ...

class serialReply(_message.Message):
    __slots__ = ("mineSerial",)
    MINESERIAL_FIELD_NUMBER: _ClassVar[int]
    mineSerial: str
    def __init__(self, mineSerial: _Optional[str] = ...) -> None: ...
