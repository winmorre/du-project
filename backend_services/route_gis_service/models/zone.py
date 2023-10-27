import datetime
from typing import Dict, Any, List,Tuple

from dataclasses_json import dataclass_json
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
@dataclass_json
class Zone(BaseModel):
    _id: str
    id: int
    createdAt: datetime.datetime
    polygon: List[Tuple]
    zoneId: str
    entities: Dict[str, Any]  # this will contain landmarks, city,streets etc

    class Config:
        schema_extra = {
            "example": {
                "id": 100,
                "createdAt": "2023-10-11",
                "polygon": [
                    {
                        "lat": 1.098,
                        "lng": -0.567
                    },
                ],
                "zoneId": "AC8976",
                "entities": {
                    "city": "Accra",
                    "landmark": "Ashongman Melcom",
                    "localName": "Musuku",
                    "radius":590.0,
                }
            }
        }

