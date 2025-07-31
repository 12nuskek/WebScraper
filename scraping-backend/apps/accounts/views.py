from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter, OpenApiResponse
from .models import User, Profile
from .serializers import UserRegistrationSerializer, ProfileSerializer


@extend_schema(
    tags=['Auth'],
    summary='Register a new user',
    description='Create a new user account with email and password',
    responses={
        201: OpenApiResponse(description='User registered successfully'),
        400: OpenApiResponse(description='Validation errors'),
    }
)
class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                'message': 'User registered successfully',
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=['Auth'],
    summary='Login user',
    description='Authenticate user and obtain JWT access and refresh tokens',
    responses={
        200: OpenApiResponse(description='Login successful, tokens returned'),
        401: OpenApiResponse(description='Invalid credentials'),
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view that returns user info along with tokens."""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            email = request.data.get('email')
            try:
                user = User.objects.get(email=email)
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
                response.data['user'] = user_data
            except User.DoesNotExist:
                pass
        
        return response


@extend_schema(
    tags=['Auth'],
    summary='Logout user',
    description='Blacklist the refresh token to logout the user',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string', 'description': 'Refresh token to blacklist'}
            },
            'required': ['refresh']
        }
    },
    responses={
        200: OpenApiResponse(description='Successfully logged out'),
        400: OpenApiResponse(description='Invalid or missing refresh token'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout endpoint that blacklists the refresh token."""
    
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except TokenError:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    list=extend_schema(
        tags=['Profiles'],
        summary='Get current user profile',
        description='Retrieve the current authenticated user\'s profile information',
        responses={200: ProfileSerializer}
    ),
    update=extend_schema(
        tags=['Profiles'],
        summary='Update current user profile',
        description='Update the current authenticated user\'s profile information',
        responses={200: ProfileSerializer}
    ),
    partial_update=extend_schema(
        tags=['Profiles'],
        summary='Partially update current user profile',
        description='Partially update the current authenticated user\'s profile information',
        responses={200: ProfileSerializer}
    )
)
class ProfileViewSet(ModelViewSet):
    """ViewSet for user profile management."""
    
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's profile."""
        return Profile.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get the current user's profile."""
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def list(self, request, *args, **kwargs):
        """Return the current user's profile as 'me' endpoint."""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update the current user's profile."""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update of the current user's profile."""
        return self.update(request, *args, **kwargs)