from rest_framework.serializers import ModelSerializer, as_serializer_error

from account.models import Team


class TeamCreateSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = ("teamName",)


class TeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"
