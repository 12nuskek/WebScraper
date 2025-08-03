# WebScraper - Django REST API Backend

A comprehensive web scraping platform built with Django REST Framework, featuring job queuing, worker processing, and complete API documentation.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Virtual environment support
- Git

### 1. Clone and Setup
```bash
git clone https://github.com/12nuskek/WebScraper.git
cd WebScraper

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r scraping-backend/requirements.txt

# Run migrations
cd scraping-backend
python manage.py migrate


```

### 2. Start the Backend Server
```bash
# From WebScraper/scraping-backend directory
python manage.py runserver
```
🌐 **Backend runs on:** http://127.0.0.1:8000/

### 3. Start the Worker (In Same Virtual Environment)
Open a new terminal and:
```bash
cd WebScraper
source venv/bin/activate  # Activate same virtual environment

# Start the worker
cd scraping-backend/services/worker
python run_worker.py


```

🔧 **Worker will poll for jobs every 5 seconds**

---

## 📁 Project Structure

```
WebScraper/
├── scraping-backend/              # Main Django project
│   ├── apps/                      # All custom applications
│   │   ├── auth/                  # User authentication & profiles
│   │   ├── projects/              # Project management
│   │   ├── spider/                # Spider/scraper configuration
│   │   ├── job/                   # Job management & queuing
│   │   ├── request/               # HTTP request queue
│   │   ├── response/              # HTTP response storage
│   │   ├── schedule/              # Cron-based job scheduling
│   │   ├── session/               # Session management
│   │   ├── proxy/                 # Proxy configuration
│   │   └── core/                  # Core utilities
│   ├── config/                    # Django settings
│   │   ├── settings/
│   │   │   ├── base.py           # Base settings
│   │   │   ├── local.py          # Development settings
│   │   │   └── prod.py           # Production settings
│   │   ├── urls.py               # Main URL configuration
│   │   └── wsgi.py              # WSGI application
│   ├── services/                  # Background services
│   │   └── worker/               # Job processing worker
│   │       ├── basic_worker.py   # Main worker implementation
│   │       ├── run_worker.py     # Worker CLI interface
│   │       └── start_worker.sh   # Worker startup script
│   ├── media/                    # File uploads & job results
│   ├── manage.py                 # Django management
│   └── requirements.txt          # Python dependencies
├── database/                     # Consolidated migrations
│   └── migrations/               # Migration files by app
├── tests/                        # Centralized test suite
│   ├── test_*.py                # Individual test files
│   ├── run_tests.py             # Test runner
│   └── README.md                # Testing documentation
├── venv/                         # Virtual environment
└── README.md                     # This file
```

---

## 🔌 API Endpoints

### Base URL: `http://127.0.0.1:8000`

### 🔐 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | User registration |
| POST | `/auth/login/` | JWT login |
| POST | `/auth/logout/` | Logout |
| POST | `/auth/token/refresh/` | Refresh JWT token |
| GET,PUT,PATCH | `/profiles/me/` | User profile management |

### 📁 Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET,POST | `/projects/` | List/create projects |
| GET,PUT,PATCH,DELETE | `/projects/{id}/` | Project CRUD operations |

### 🕷️ Spiders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET,POST | `/spiders/` | List/create spiders |
| GET,PUT,PATCH,DELETE | `/spiders/{id}/` | Spider CRUD operations |

### 🔄 Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET,POST | `/jobs/` | List/create jobs |
| GET,PUT,PATCH,DELETE | `/jobs/{id}/` | Job CRUD operations |

### 📨 Requests (HTTP Queue)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET,POST | `/requests/` | List/create HTTP requests |
| GET,PUT,PATCH,DELETE | `/requests/{id}/` | Request CRUD operations |
| POST | `/requests/{id}/mark_in_progress/` | Mark request as in progress |
| POST | `/requests/{id}/mark_done/` | Mark request as completed |
| POST | `/requests/{id}/mark_error/` | Mark request as failed |
| POST | `/requests/{id}/retry/` | Retry failed request |
| GET | `/requests/next_pending/` | Get next pending request (for workers) |

### 📥 Responses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET,POST | `/responses/` | List/create responses |
| GET,PUT,PATCH,DELETE | `/responses/{id}/` | Response CRUD operations |
| GET | `/responses/{id}/body/` | Download response body |
| POST | `/responses/{id}/save_body/` | Save response body content |
| GET | `/responses/stats/` | Response statistics |
| GET | `/responses/successful/` | List successful responses |
| GET | `/responses/errors/` | List error responses |

### ⏰ Schedules
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET,POST | `/schedules/` | List/create schedules |
| GET,PUT,PATCH,DELETE | `/schedules/{id}/` | Schedule CRUD operations |
| POST | `/schedules/{id}/enable/` | Enable schedule |
| POST | `/schedules/{id}/disable/` | Disable schedule |
| POST | `/schedules/{id}/mark_executed/` | Mark as executed |
| POST | `/schedules/{id}/recalculate/` | Recalculate next run |
| GET | `/schedules/due/` | Get due schedules |
| GET | `/schedules/upcoming/` | Get upcoming schedules |
| GET | `/schedules/stats/` | Schedule statistics |
| GET | `/schedules/cron_help/` | Cron expression help |

### 🌐 Sessions & Proxies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET,POST | `/sessions/` | List/create sessions |
| GET,PUT,PATCH,DELETE | `/sessions/{id}/` | Session CRUD operations |
| GET,POST | `/proxies/` | List/create proxies |
| GET,PUT,PATCH,DELETE | `/proxies/{id}/` | Proxy CRUD operations |

---

## 📚 API Documentation

Interactive API documentation is available when the server is running:

- **Swagger UI**: http://127.0.0.1:8000/docs/
- **ReDoc**: http://127.0.0.1:8000/redoc/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

---

## 🧪 Testing

This project has **comprehensive test coverage** with **408 tests** covering all functionality.

### Run All Tests
```bash
# From project root
python tests/run_tests.py

# With verbose output
python tests/run_tests.py -v 2

# Run specific test file
python tests/run_tests.py test_worker
```

### Run Django Tests
```bash
# From scraping-backend directory
python manage.py test tests
```

### Test Coverage
- ✅ **389 core tests** - Models, views, serializers, authentication
- ✅ **19 worker tests** - Job processing, error handling, integration
- ✅ **Complete API coverage** - All endpoints tested
- ✅ **Error scenarios** - Edge cases and failure handling

---

## 🛠️ Development Workflow: Adding New Apps

This project follows a **test-driven development** approach with consolidated migrations.

### 1. Create App Structure
```bash
cd scraping-backend/apps
mkdir your_new_app
cd your_new_app

# Create required files
touch __init__.py models.py views.py serializers.py urls.py admin.py apps.py
```

### 2. Write Tests First
```bash
# Create test file in tests directory
touch ../../tests/test_your_new_app_model.py
touch ../../tests/test_your_new_app_views.py
touch ../../tests/test_your_new_app_serializers.py
```

**Example test structure:**
```python
# tests/test_your_new_app_model.py
from django.test import TestCase
from apps.your_new_app.models import YourModel

class YourModelTest(TestCase):
    def test_model_creation(self):
        # Write failing test first
        pass
```

### 3. Implement Models
```python
# apps/your_new_app/models.py
from django.db import models

class YourModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 4. Create Migration (Consolidated)
```bash
# From scraping-backend directory
python manage.py makemigrations your_new_app

# Move migration to consolidated location
mkdir -p ../database/migrations/your_new_app
mv apps/your_new_app/migrations/0001_initial.py ../database/migrations/your_new_app/
```

### 5. Implement Views and Serializers
```python
# apps/your_new_app/serializers.py
from rest_framework import serializers
from .models import YourModel

class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = '__all__'

# apps/your_new_app/views.py
from rest_framework import viewsets
from .models import YourModel
from .serializers import YourModelSerializer

class YourModelViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
```

### 6. Add URLs
```python
# apps/your_new_app/urls.py
from rest_framework.routers import DefaultRouter
from .views import YourModelViewSet

router = DefaultRouter()
router.register(r"your-models", YourModelViewSet, basename="your-model")
urlpatterns = router.urls

# Add to scraping-backend/config/urls.py
urlpatterns = [
    # ... existing patterns
    path('', include('apps.your_new_app.urls')),
]
```

### 7. Iterate with Tests
```bash
# Run tests to check implementation
python tests/run_tests.py test_your_new_app

# Fix any failing tests, then run all tests
python tests/run_tests.py
```

### 8. Register App
```python
# scraping-backend/config/settings/base.py
INSTALLED_APPS = [
    # ... existing apps
    'apps.your_new_app',
]
```

### 9. Apply Migrations
```bash
python manage.py migrate
```

### 10. Verify Integration
```bash
# Run full test suite
python tests/run_tests.py

# Test API endpoints
curl http://127.0.0.1:8000/your-models/
```

---

## 🔧 Worker System

The worker system processes jobs asynchronously:

### How It Works
1. **Job Creation**: Create jobs via API (`POST /jobs/`)
2. **Worker Polling**: Worker checks for `queued` jobs every 5 seconds
3. **Job Processing**: Worker updates job status (`running` → `done`/`failed`)
4. **Result Storage**: Results saved to `media/job_results/`

### Worker Configuration
```python
# scraping-backend/services/worker/basic_worker.py
worker = BasicWorker(poll_interval=5)  # Check every 5 seconds
worker.start()
```

### Monitoring Worker
```bash
# View worker output
cd scraping-backend/services/worker
python run_worker.py

# Worker shows:
# 📊 Jobs: Total=5, Queued=2, Running=1, Done=2, Failed=0
# 🔸 PROCESSING JOB 123
# ✅ Job 123 completed
```

---

## 🔐 Authentication

The API uses **JWT (JSON Web Tokens)** for authentication:

### Login Flow
```bash
# 1. Register user
curl -X POST http://127.0.0.1:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secure123","first_name":"John","last_name":"Doe"}'

# 2. Login to get tokens
curl -X POST http://127.0.0.1:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secure123"}'

# Response includes access and refresh tokens
```

### Making Authenticated Requests
```bash
# Include JWT token in Authorization header
curl -X GET http://127.0.0.1:8000/projects/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📊 Database Schema

The project uses **consolidated migrations** for better organization:

### Migration Structure
```
database/
└── migrations/
    ├── auth/0001_initial.py          # User authentication
    ├── projects/0001_initial.py      # Project management
    ├── spider/0001_initial.py        # Spider configuration
    ├── job/0001_initial.py           # Job management
    ├── request/0001_initial.py       # HTTP request queue
    ├── response/0001_initial.py      # HTTP response storage
    ├── schedule/0001_initial.py      # Job scheduling
    ├── session/0001_initial.py       # Session management
    └── proxy/0001_initial.py         # Proxy configuration
```

### Key Relationships
- **User** → **Projects** (1:many)
- **Project** → **Spiders** (1:many)
- **Spider** → **Jobs** (1:many)
- **Job** → **Requests** (1:many)
- **Request** → **Responses** (1:many)
- **Spider** → **Schedules** (1:many)

---

## 🚀 Production Deployment

### Environment Variables
```bash
# Set in production
export DJANGO_SETTINGS_MODULE=config.settings.prod
export SECRET_KEY=your-secret-key
export DATABASE_URL=your-database-url
export DEBUG=False
```

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up static file serving
- [ ] Configure logging
- [ ] Set up monitoring for worker processes
- [ ] Secure JWT secret keys
- [ ] Configure CORS settings
- [ ] Set up SSL/HTTPS

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Write tests first** (TDD approach)
4. **Implement feature**
5. **Run test suite**: `python tests/run_tests.py`
6. **Commit changes**: `git commit -m "Add your feature"`
7. **Push to branch**: `git push origin feature/your-feature`
8. **Create Pull Request**

### Code Standards
- Follow **TDD** (Test-Driven Development)
- Maintain **100% test coverage** for new features
- Use **consolidated migrations** in `database/migrations/`
- Document **API endpoints** with `drf-spectacular`
- Follow **Django REST Framework** conventions

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Common Issues

**Worker not processing jobs?**
- Check worker is running: `ps aux | grep worker`
- Verify database connection in worker
- Check job status: `GET /jobs/`

**Authentication errors?**
- Verify JWT token is valid
- Check token expiration
- Refresh token if needed: `POST /auth/token/refresh/`

**Migration errors?**
- Check migrations are in correct location: `database/migrations/`
- Run: `python manage.py migrate`
- Check for migration conflicts

### Getting Help
- 📚 Check API docs: http://127.0.0.1:8000/docs/
- 🧪 Run tests: `python tests/run_tests.py -v 2`
- 📋 Check logs in Django admin
- 🔍 Review existing test files for examples

---

**Made with ❤️ using Django REST Framework**