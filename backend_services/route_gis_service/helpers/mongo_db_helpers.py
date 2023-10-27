import motor.motor_asyncio

from configs.settings import get_settings
from models.zone import Zone

_settings = get_settings()


def get_mongo_client(mongo_uri: str = _settings.mongodb_uri):
    return motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)


def map_document_to_zone(document: dict) -> Zone:
    return Zone(
        _id=document["_id"],
        id=document["id"],
        createdAt=document.get("createdAt"),
        polygon=document.get("polygon"),
        zoneId=document.get("zoneId"),
        entities=document.get("entities"),
    )
