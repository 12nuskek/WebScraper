from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProxyViewSet

router = DefaultRouter()
router.register(r'proxies', ProxyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]