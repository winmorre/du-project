from http import HTTPStatus

from rest_framework.viewsets import ViewSet
from rest_framework.request import Request

from team.models import Team
from serializers.team_serializer import TeamSerializer
from factories.service_factory import ServiceFactory
from helpers import view_helpers as vh


class TeamViewSet(ViewSet):
    team_service = ServiceFactory.create_team_service()
    query = Team.objects.all()
    serializer = TeamSerializer

    def list(self, request):
        result = self.team_service.get_all_teams()
        if vh.check_error_response_instance(result):
            return vh.error_response(result.asdict())

        return vh.success_response(data=result)

    def retrieve(self, request: Request, pk=None, team_name=None):
        result = self.team_service.get_team(pk=pk, team_name=team_name)
        if vh.check_error_response_instance(result):
            return vh.error_response(result.asdict())

        return vh.success_response(result)

    def create(self, request: Request):
        result = self.team_service.create_team(payload=request.data)
        if vh.check_error_response_instance(result):
            return vh.error_response(result.asdict(), status_code=HTTPStatus.CREATED)

        return vh.success_response(result, )

    def assign_zones(self, request: Request):
        data = request.data
        result = self.team_service.assign_zones(pk=data["pk"], zones=data["zones"])

        if vh.check_error_response_instance(result):
            return vh.error_response(result.asdict())

        return vh.success_response(result)

    def remove_zone(self, request: Request):
        data = request.data
        result = self.team_service.remove_assigned_zones(pk=data["pk"], zone=data["zone"])
        if vh.check_error_response_instance(result):
            return vh.error_response(result.asdict())

        return vh.success_response(result)
