import secrets
import string

from bson.son import SON

from repositories.zone_repository import ZoneRepository
from libs.id_gen import id_gen


class ZoneService:
    def __init__(self, zone_repo: ZoneRepository):
        self.__zone_repo = zone_repo

    async def add_zone(self, data: dict):
        zone_id = self._generate_zone_id()
        zone = self.get_zone(zone_id=zone_id)
        if zone is not None:
            await self.add_zone(data=data)

        data_polygon = data["polygon"]
        new_polygon = []
        for item in data_polygon:
            new_polygon.append(SON([("lat", item[0]), ("lng", item[1])]))

        data["polygon"] = new_polygon
        data["zoneId"] = zone_id
        new_zone = self.__zone_repo.add_zone(data)
        return new_zone

    def get_zone_by_coordinate(self):
        ...

    def get_zones(self):
        return self.__zone_repo.retrieve_zones()

    def get_zone(self, id=None, zone_id=None):
        return self.__zone_repo.retrieve_zone(id=id, zone_id=zone_id)

    def update_zone(self, id, data):
        return self.__zone_repo.update_zone(id=id, data=data)

    def delete_zone(self, id=None, zone_id=None):
        return self.__zone_repo.delete_zone(id=id, zone_id=zone_id)

    def _generate_zone_id(self):
        alphabet = string.ascii_lowercase + str(id_gen.get_id())

        return ''.join(secrets.choice(alphabet) for _ in range(6)).upper()
