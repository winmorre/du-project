from dataclasses_json import dataclass_json
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass_json
@dataclass
class ErrorResponse(BaseModel, serializer="json"):
    title: str
    type: str
    detail: str
    reason: str | None
