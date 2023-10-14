import traceback

import structlog

from repositories.team_repository import TeamRepository
from errors.team_error import TeamError
from models.error_response import ErrorResponse

Logger = structlog.getLogger(__name__)


class TeamService:
    def __init__(self, team_repo: TeamRepository):
        self._team_repo = team_repo

    def create_team(self, payload):
        try:
            team = self._team_repo.create_team(payload)
            return team
        except TeamError as te:
            Logger.error("create team error", payload=payload, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Create team object error",
                detail=(
                    f"{te.args[0]}"
                    f"\n {traceback.format_exc()}"
                )
            )

    def get_team(self, pk=None, team_name=None):
        try:
            team, _ = self._team_repo.fetch_team(pk=pk, team_name=team_name)
            return team
        except TeamError as te:
            Logger.error("get team error", pk=pk, team_name=team_name, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Get team object error",
                detail=(
                    f"{te.args[0]}"
                    f"\n {traceback.format_exc()}"
                )
            )

    def get_all_teams(self):
        try:
            return self._team_repo.fetch_all_teams()
        except TeamError as te:
            Logger.error("get all teams error", traceback=traceback.format_exc())
            return ErrorResponse(
                title="Get all teams error",
                detail=(
                    f"{te.args[0]}"
                    f"\n {traceback.format_exc()}"
                )
            )

    def assign_zones(self, pk, zones):
        try:
            return self._team_repo.assign_zones(pk=pk, zone=zones)
        except TeamError as te:
            Logger.error("assign zones error", traceback=traceback.format_exc())
            return ErrorResponse(
                title="Assign zone error",
                detail=(
                    f"{te.args[0]}"
                    f"\n {traceback.format_exc()}"
                )
            )

    def remove_assigned_zones(self, zone, pk):
        try:
            return self._team_repo.remove_assigned_zone(pk=pk, zone=zone)
        except TeamError as te:
            Logger.error("remove assigned zones error", traceback=traceback.format_exc())
            return ErrorResponse(
                title="remove assigned zone error",
                detail=(
                    f"{te.args[0]}"
                    f"\n {traceback.format_exc()}"
                )
            )
