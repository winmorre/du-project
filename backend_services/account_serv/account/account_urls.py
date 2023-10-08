from factories.view_factory import ViewFactory
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", ViewFactory.create_account_viewset(), basename="")

urlpatterns = []

urlpatterns += router.urls
