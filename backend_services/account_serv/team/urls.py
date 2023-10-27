from django.urls import path
from team.views import TeamViewSet

urlpatterns = [
    path("/", TeamViewSet.as_view({"post": "create"})),
    path("/", TeamViewSet.as_view({"get": "list"})),
    path("/<pk>", TeamViewSet.as_view({"get": "retrieve"})),
    path("/assign-zones", TeamViewSet.as_view({"post": "assign_zones"})),
    path("/remove-zone", TeamViewSet.as_view({"delete": "remove_zone"})),
]
