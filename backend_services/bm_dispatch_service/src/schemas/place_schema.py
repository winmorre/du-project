from pydantic import BaseModel
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class PlaceSchema(BaseModel):
    id: str
    url: str | None
    placeType: str
    name: str
    fullname: str
    countryCode: str
    country: str
    boundingBox: dict
