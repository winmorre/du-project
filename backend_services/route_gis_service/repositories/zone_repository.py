from typing import List

from bson.objectid import ObjectId

from helpers import mongo_db_helpers as mh
from models.zone import Zone


class ZoneRepository:
    def __init__(self, mongo_client):
        self.__client = mongo_client
        self.__db = self._get_db()
        self.__collection = self._get_collection()

    def _get_db(self):
        return self.__client.zones

    def _get_collection(self):
        return self.__db.get_collection("zones")

    async def retrieve_zones(self) -> List[Zone]:
        cursor = await self.__collection.find()
        return [mh.map_document_to_zone(z) for z in cursor]

    async def retrieve_zone(self, id=None, zone_id=None) -> Zone | None:
        zone = await self._get_zone(id=id, zone_id=zone_id)
        if not zone:
            return None
        return mh.map_document_to_zone(zone)

    async def add_zone(self, zone: dict):
        zone = await self.__collection.insert_one(zone)
        new_zone = await self.__collection.find_one({"id": zone["id"]})
        return mh.map_document_to_zone(new_zone)

    async def update_zone(self, id: int, data: dict) -> bool:
        zone = await self.__collection.find_one({"id": id})
        if not zone:
            return False
        updated_zone = await self.__collection.update_one({"id": id}, {"$set": data})
        if not updated_zone:
            return False
        return True

    async def delete_zone(self, id=None, zone_id=None):
        zone = await self._get_zone(id=id, zone_id=zone_id)

        if zone:
            await self.__collection.delete_one({"_id": ObjectId(zone["_id"])})
            return True

        return False

    async def _get_zone(self, id=None, zone_id=None):
        if id is None and zone_id is None:
            raise ValueError("Specify value for one of id or zone_id")

        zone = None
        if id:
            zone = await self.__collection.find_one({"id": id})
        else:
            zone = await self.__collection.find_one({"zoneId": zone_id})

        return zone
