from rest_framework.routers import DefaultRouter
from .views import RequestQueueViewSet

router = DefaultRouter()
router.register(r"requests", RequestQueueViewSet, basename="request")

urlpatterns = router.urls