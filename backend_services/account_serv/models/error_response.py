from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class ErrorResponse:
    title: str
    type: str
    detail: str
    reason: str | None
