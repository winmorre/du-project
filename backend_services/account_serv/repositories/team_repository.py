import datetime
from typing import Type

from team.models import Team
from helpers import validators_helpers as vh
from libs.id_gen import id_gen
from errors.team_error import TeamError
from serializers.team_serializer import TeamSerializer, TeamCreateSerializer


class TeamRepository:
    def __init__(
            self, team: Type[Team], team_create_serializer: Type[TeamCreateSerializer],
            team_serializer: Type[TeamSerializer],
    ):
        self._team = team
        self._team_serializer = team_serializer
        self._team_create_serializer = team_create_serializer

    def create_team(self, payload: dict):
        try:
            serializer = self._team_create_serializer(data=payload)
            if not vh.is_valid_serializer(serializer):
                raise TeamError(str(serializer.errors))

            now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)
            serializer.save(createdAt=now, id=id_gen.get_id())

            return serializer.data
        except Exception:
            raise TeamError("Could not create team")

    def fetch_team(self, pk=None, team_name=None):
        if pk is None and team_name is None:
            raise TeamError("Provide either a team ID or team Name")

        try:
            if pk:
                team = self._team.objects.get(id=pk)
                if team is None:
                    raise TeamError(f"Team with ID {pk} does not exist")

                return self._team_serializer(team).data

            if team_name:
                team = self._team.objects.get(teamName=team_name)
                if team is None:
                    raise TeamError(f"Team with name {team_name} does not exist")

                return self._team_serializer(team).data, team
        except Exception:
            raise TeamError("Could not fetch team")

    def fetch_all_teams(self):
        try:
            teams = self._team.objects.all()
            return self._team_serializer(teams, many=True).data
        except Exception:
            raise TeamError("Couldn't fetch all teams")

    def assign_zones(self, pk, zone):
        """
        assign zones
        :param pk
        :param zone: This can be a list of zones concatenated by ';'
        """
        try:
            team = self._team.objects.get(id=pk)
            if team is None:
                raise TeamError(f"Team with ID {pk} does not exist")

            team_zone = team.assignedZones
            if team_zone is None or team_zone == "":
                setattr(team, "assignedZones", zone)
            else:
                setattr(team, "assignedZones", team.assignedZones + ";" + zone)

            team.save()
            return self._team_serializer(team).data
        except Exception:
            raise TeamError("Couldn't assign zone")

    def remove_assigned_zone(self, pk, zone):
        try:
            team: Team | None = self._team.objects.get(id=pk)
            if team is None:
                raise TeamError(f"Team with ID {pk} does not exist")

            team_zones = team.assignedZones.split(";")
            team_zones = ';'.join(list(filter(lambda t: t != zone, team_zones)))
            team.assignedZones = team_zones
            team.save(update_fields=["assignedZones"])
            return self._team_serializer(team).data
        except Exception:
            raise TeamError(f"Could not remove assigned zone {zone}")

    def delete_team(self, pk=None, team_name=None):
        try:
            _, team = self.fetch_team(pk=pk, team_name=team_name)
            team.delete()
            return True
        except Exception:
            raise TeamError("Couldn't delete team")
