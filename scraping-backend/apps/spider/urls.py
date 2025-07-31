from rest_framework.routers import DefaultRouter
from .views import SpiderViewSet

router = DefaultRouter()
router.register(r"spiders", SpiderViewSet, basename="spider")

urlpatterns = router.urls