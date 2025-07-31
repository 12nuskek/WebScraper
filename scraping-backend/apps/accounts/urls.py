from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiResponse
from .views import (
    RegisterView, 
    CustomTokenObtainPairView, 
    logout_view, 
    ProfileViewSet
)

# Create a tagged version of TokenRefreshView
@extend_schema(
    tags=['Auth'],
    summary='Refresh access token',
    description='Obtain a new access token using a valid refresh token',
    responses={
        200: OpenApiResponse(description='New access token generated'),
        401: OpenApiResponse(description='Invalid refresh token'),
    }
)
class TaggedTokenRefreshView(TokenRefreshView):
    pass

# Create router for viewsets
router = DefaultRouter()

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/token/refresh/', TaggedTokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile endpoints
    path('profiles/me/', ProfileViewSet.as_view({
        'get': 'list',
        'put': 'update',
        'patch': 'partial_update'
    }), name='profile-me'),
    
    # Include router URLs
    path('', include(router.urls)),
]