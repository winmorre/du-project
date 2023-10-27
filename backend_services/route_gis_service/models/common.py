from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass
@dataclass_json
class Response:
    data: list
    code: int
    message: str | None


@dataclass
@dataclass_json
class ErrorResponse:
    error: str
    code: int
    message: str
