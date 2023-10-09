# from factories.view_factory import ViewFactory
from rest_framework import routers
from account.views import AccountViewSet

router = routers.DefaultRouter()
router.register("", AccountViewSet, basename="")

urlpatterns = []

urlpatterns += router.urls
