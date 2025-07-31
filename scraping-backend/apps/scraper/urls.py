from rest_framework.routers import DefaultRouter
from .views import SpiderViewSet

router = DefaultRouter()
# Using <int:pk> pattern to fix the path parameter type warning
router.register(r"spiders", SpiderViewSet, basename="spider")

urlpatterns = router.urls