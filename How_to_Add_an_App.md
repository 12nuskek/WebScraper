# How to Add a New App to the WebScraper Django Project

## Project Overview

This Django project follows a custom structure optimized for web scraping applications with:
- **Django REST Framework** for API endpoints
- **JWT Authentication** for security
- **Consolidated migrations** in a separate database directory
- **Centralized testing** structure
- **API documentation** with drf-spectacular

## Project Structure

```
WebScraper/
├── scraping-backend/           # Main Django project
│   ├── apps/                   # All custom apps
│   ├── config/                 # Django settings and configuration
│   ├── manage.py              # Django management command
│   └── requirements.txt       # Project dependencies
├── database/                  # Consolidated database migrations
├── tests/                     # Centralized test files
└── venv/                      # Virtual environment
```

## Prerequisites

Before adding a new app, ensure you have:
1. **Virtual environment activated**: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
2. **Dependencies installed**: `pip install -r scraping-backend/requirements.txt`
3. **Understanding of the project's API patterns**

## Step-by-Step Guide to Add a New App

### Step 1: Create the App Structure

Navigate to the apps directory and create your new app:

```bash
cd scraping-backend/apps
mkdir your_new_app
cd your_new_app
```

Create the following files in your new app directory:

```bash
touch __init__.py
touch apps.py
touch models.py
touch views.py
touch serializers.py
touch urls.py
touch admin.py
```

### Step 2: Configure the App (apps.py)

Create the app configuration in `apps/your_new_app/apps.py`:

```python
from django.apps import AppConfig


class YourNewAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.your_new_app'
    # Add label if there are naming conflicts
    # label = 'your_custom_label'
```

### Step 3: Add App to Django Settings

Edit `scraping-backend/config/settings/base.py` and add your app to the `LOCAL_APPS` list:

```python
LOCAL_APPS = [
    'apps.core',
    'apps.auth',
    'apps.profiles',
    'apps.projects',
    'apps.spider',
    'apps.job',
    'apps.request',
    'apps.response',
    'apps.schedule',
    'apps.session',
    'apps.proxy',
    'apps.your_new_app',  # Add your new app here
]
```

### Step 4: Create Models

Define your models in `apps/your_new_app/models.py`:

```python
from django.conf import settings
from django.db import models


class YourModel(models.Model):
    """
    Description of your model.
    """
    # Common pattern: owner field for user-owned resources
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="your_models",
    )
    
    # Your specific fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamp fields (recommended pattern)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Your Model"
        verbose_name_plural = "Your Models"

    def __str__(self):
        return self.name
```

### Step 5: Create Serializers

Define your DRF serializers in `apps/your_new_app/serializers.py`:

```python
from rest_framework import serializers
from .models import YourModel


class YourModelSerializer(serializers.ModelSerializer):
    """Serializer for YourModel."""
    
    # Hide owner field and auto-assign current user
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = YourModel
        fields = (
            "id", 
            "name", 
            "description", 
            "is_active", 
            "created_at", 
            "updated_at", 
            "owner"
        )
        read_only_fields = ("id", "created_at", "updated_at", "owner")

    def validate_name(self, value):
        """Custom validation for name field."""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()
```

### Step 6: Create Views

Define your API views in `apps/your_new_app/views.py`:

```python
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import YourModel
from .serializers import YourModelSerializer


class YourModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing YourModel instances.
    
    Provides CRUD operations and additional custom actions.
    """
    serializer_class = YourModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'created_at']
    search_fields = ['name', 'description']

    def get_queryset(self):
        """Return objects owned by the current user."""
        return YourModel.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Set the owner to the current user when creating."""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Custom action to activate a model instance."""
        instance = self.get_object()
        instance.is_active = True
        instance.save()
        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Custom action to deactivate a model instance."""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({'status': 'deactivated'})
```

### Step 7: Configure URLs

Create URL routing in `apps/your_new_app/urls.py`:

```python
from rest_framework.routers import DefaultRouter
from .views import YourModelViewSet

router = DefaultRouter()
router.register(r"your-models", YourModelViewSet, basename="yourmodel")

urlpatterns = router.urls
```

### Step 8: Add URLs to Main Configuration

Edit `scraping-backend/config/urls.py` to include your app's URLs:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('', include('apps.auth.urls')),
    path('', include('apps.projects.urls')),
    path('', include('apps.spider.urls')),
    path('', include('apps.job.urls')),
    path('', include('apps.request.urls')),
    path('', include('apps.response.urls')),
    path('', include('apps.schedule.urls')),
    path('', include('apps.session.urls')),
    path('', include('apps.proxy.urls')),
    path('', include('apps.your_new_app.urls')),  # Add this line
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

### Step 9: Configure Admin Interface

Set up Django admin in `apps/your_new_app/admin.py`:

```python
from django.contrib import admin
from .models import YourModel


@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    """Admin configuration for YourModel."""
    
    list_display = ('name', 'owner', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'owner')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Customize queryset for better performance."""
        return super().get_queryset(request).select_related('owner')
```

### Step 10: Create Migration Directory

Create the migration directory structure in the database folder:

```bash
mkdir -p database/migrations/your_new_app
touch database/migrations/your_new_app/__init__.py
```

### Step 11: Generate and Run Migrations

Generate migrations for your new app:

```bash
cd scraping-backend
python manage.py makemigrations your_new_app
python manage.py migrate
```

**Note**: Due to the custom migration setup, migrations will be stored in `database/migrations/your_new_app/` instead of the default location.

### Step 12: Create Tests

Create comprehensive tests in `tests/test_your_new_app_models.py`:

```python
"""
Tests for YourNewApp models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.your_new_app.models import YourModel
from .test_core import BaseTestCase

User = get_user_model()


class YourModelTestCase(BaseTestCase):
    """Tests for YourModel."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.model_data = {
            'name': 'Test Model',
            'description': 'Test description',
            'owner': self.user
        }

    def test_create_model(self):
        """Test creating a YourModel instance."""
        model = YourModel.objects.create(**self.model_data)
        self.assertEqual(model.name, 'Test Model')
        self.assertEqual(model.owner, self.user)
        self.assertTrue(model.is_active)

    def test_model_string_representation(self):
        """Test the string representation of YourModel."""
        model = YourModel.objects.create(**self.model_data)
        self.assertEqual(str(model), 'Test Model')

    def test_model_ordering(self):
        """Test that models are ordered by creation date (newest first)."""
        model1 = YourModel.objects.create(name='First', owner=self.user)
        model2 = YourModel.objects.create(name='Second', owner=self.user)
        
        models = YourModel.objects.all()
        self.assertEqual(models.first(), model2)
        self.assertEqual(models.last(), model1)
```

Create API tests in `tests/test_your_new_app_views.py`:

```python
"""
Tests for YourNewApp API views.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.your_new_app.models import YourModel
from .test_core import BaseTestCase


class YourModelViewSetTestCase(APITestCase, BaseTestCase):
    """Tests for YourModelViewSet."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.client.force_authenticate(user=self.user)
        
        self.model = YourModel.objects.create(
            name='Test Model',
            description='Test description',
            owner=self.user
        )
        
        self.list_url = '/your-models/'
        self.detail_url = f'/your-models/{self.model.id}/'

    def test_list_models(self):
        """Test listing models."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_model(self):
        """Test creating a new model."""
        data = {
            'name': 'New Model',
            'description': 'New description',
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(YourModel.objects.count(), 2)

    def test_retrieve_model(self):
        """Test retrieving a specific model."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Model')

    def test_update_model(self):
        """Test updating a model."""
        data = {'name': 'Updated Model'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.model.refresh_from_db()
        self.assertEqual(self.model.name, 'Updated Model')

    def test_delete_model(self):
        """Test deleting a model."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(YourModel.objects.count(), 0)

    def test_activate_action(self):
        """Test the activate custom action."""
        self.model.is_active = False
        self.model.save()
        
        url = f'{self.detail_url}activate/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.model.refresh_from_db()
        self.assertTrue(self.model.is_active)
```

### Step 13: Run Tests

Run your tests to ensure everything works:

```bash
cd tests
python run_tests.py test_your_new_app_models
python run_tests.py test_your_new_app_views
```

### Step 14: Update API Documentation

The API documentation will automatically include your new endpoints thanks to drf-spectacular. You can view it at:
- Swagger UI: `http://localhost:8000/docs/`
- ReDoc: `http://localhost:8000/redoc/`

## Best Practices

### 1. Model Design
- Always include `created_at` and `updated_at` timestamp fields
- Use `owner` field for user-owned resources
- Add proper `Meta` class with ordering and verbose names
- Implement meaningful `__str__` methods

### 2. Serializers
- Use `HiddenField` with `CurrentUserDefault()` for owner fields
- Add custom validation methods when needed
- Use `read_only_fields` for fields that shouldn't be modified

### 3. Views
- Filter querysets by user ownership for security
- Use proper permission classes
- Add custom actions for specific business logic
- Include filtering and search capabilities

### 4. URLs
- Use descriptive URL patterns (kebab-case)
- Follow RESTful conventions
- Use meaningful basename for routers

### 5. Testing
- Test all CRUD operations
- Test custom actions and business logic
- Test permission and authorization
- Use the BaseTestCase for common utilities

### 6. Admin
- Configure list_display, list_filter, and search_fields
- Use fieldsets for organized admin interface
- Optimize querysets with select_related/prefetch_related

## Common Pitfalls to Avoid

1. **Forgetting to add the app to settings**: Always add new apps to `LOCAL_APPS`
2. **Migration issues**: Ensure migration directory exists in `database/migrations/`
3. **Permission problems**: Always filter querysets by user ownership
4. **Missing tests**: Write comprehensive tests for all functionality
5. **URL conflicts**: Use unique URL patterns to avoid conflicts

## Example API Usage

Once your app is set up, you can interact with it via the API:

```bash
# List all models
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/your-models/

# Create a new model
curl -X POST -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Model", "description": "Model description"}' \
     http://localhost:8000/your-models/

# Update a model
curl -X PATCH -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Updated Name"}' \
     http://localhost:8000/your-models/1/

# Activate a model (custom action)
curl -X POST -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/your-models/1/activate/
```

## Conclusion

Following this guide will ensure your new app integrates seamlessly with the existing WebScraper project architecture. The pattern emphasizes:
- **Security** through proper authentication and authorization
- **Consistency** with established coding patterns
- **Maintainability** through comprehensive testing
- **Documentation** through automatic API schema generation

Remember to always test your implementation thoroughly and follow the existing code style and patterns used throughout the project.