from django.urls import path
from factories.view_factory import ViewFactory
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("access/", ViewFactory.create_token_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view()),
]
