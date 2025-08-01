# Worker App - Celery + Redis Implementation

This app provides asynchronous job processing using Celery and Redis for the web scraping platform.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django API    │───▶│   Redis Broker  │───▶│  Celery Worker  │
│   (Job Queue)   │    │   (Message Q)   │    │ (Job Processor) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │  Celery Beat    │    │   Task Logs     │
│ (Job Storage)   │    │  (Scheduler)    │    │  (Monitoring)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Start Redis

**Windows:**
```bash
# Download Redis from https://redis.io/download
# Or use Docker:
docker run -d -p 6379:6379 redis:latest
```

**Ubuntu/Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### 3. Run Database Migrations

```bash
python manage.py migrate
python manage.py migrate django_celery_beat
python manage.py migrate django_celery_results
```

## 🎯 How to Use

### Option 1: Using Management Commands (Recommended)

**Terminal 1 - Start Celery Worker:**
```bash
python manage.py start_celery_worker
# Or with custom settings:
python manage.py start_celery_worker --concurrency 8 --loglevel DEBUG
```

**Terminal 2 - Start Celery Beat (Optional for scheduled tasks):**
```bash
python manage.py start_celery_beat
```

**Terminal 3 - Manually trigger job processing:**
```bash
python manage.py trigger_job_check
# Or check scheduled jobs too:
python manage.py trigger_job_check --check-scheduled
```

### Option 2: Direct Celery Commands

**Start Worker:**
```bash
celery -A config worker --loglevel=info --concurrency=4 --queues=job_processing,job_monitoring
```

**Start Beat Scheduler:**
```bash
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Monitor Tasks:**
```bash
celery -A config events
```

## 📋 Available Tasks

### 1. `process_job(job_id, pause_minutes=5)`
- Processes a specific job by ID
- Displays comprehensive job information
- Marks job as running → done/failed
- **Queue:** `job_processing`

### 2. `check_queued_jobs()`
- Finds next available queued job
- Automatically processes it asynchronously
- Runs every 30 seconds via Beat scheduler
- **Queue:** `job_monitoring`

### 3. `process_scheduled_jobs()`
- Checks for due scheduled jobs (cron expressions)
- Creates new job instances for due schedules
- Runs every 60 seconds via Beat scheduler
- **Queue:** `job_monitoring`

## 🔧 Configuration

### Celery Settings (in `config/settings/base.py`):

```python
# Redis Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'

# Task Configuration
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# Queue Routing
CELERY_TASK_ROUTES = {
    'apps.worker.tasks.process_job': {'queue': 'job_processing'},
    'apps.worker.tasks.check_queued_jobs': {'queue': 'job_monitoring'},
}

# Periodic Tasks
CELERY_BEAT_SCHEDULE = {
    'check-queued-jobs': {
        'task': 'apps.worker.tasks.check_queued_jobs',
        'schedule': 30.0,  # Every 30 seconds
    },
    'process-scheduled-jobs': {
        'task': 'apps.worker.tasks.process_scheduled_jobs', 
        'schedule': 60.0,  # Every minute
    },
}
```

## 📊 What Gets Printed

When a job is processed, the system displays:

```
================================================================================
JOB PROCESSING STARTED
================================================================================
PROJECT INFORMATION:
  ID: 1
  Name: E-commerce Scraper
  Owner: user@example.com
  Notes: Scraping product data
  Created: 2024-01-15 10:30:00

SPIDER INFORMATION:
  ID: 1  
  Name: product-spider
  Start URLs: ['https://example.com/products']
  Settings: {'timeout': 30, 'concurrent_requests': 16}
  Parse Rules: {'title': 'css::h1.product-title::text'}

JOB INFORMATION:
  ID: 1
  Status: running
  Started At: 2024-01-15 12:00:00
  Stats: {'requests_count': 150, 'items_scraped': 75}
  Duration: 330.0 seconds

REQUEST QUEUE INFORMATION:
  Total Requests: 150
  Status Breakdown: {'pending': 50, 'done': 95, 'error': 5}
  [Detailed request information...]

SESSION INFORMATION:
  Total Sessions: 2
  [Session details with cookies and headers...]

PROXY POOL INFORMATION:
  Total Active Proxies: 10
  Total Healthy Proxies: 8
  [Proxy health and rotation status...]

RESPONSE INFORMATION:
  Total Responses: 95
  Success (2xx): 90
  Client Errors (4xx): 3
  Server Errors (5xx): 2
  [Response performance metrics...]

SCHEDULE INFORMATION:
  Total Schedules: 1
  [Cron expressions and next run times...]
================================================================================
```

## 🔍 Monitoring

### View Task Results:
```python
from apps.worker.tasks import process_job

# Queue a job
result = process_job.delay(job_id=1)
print(f"Task ID: {result.id}")
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

### Django Admin:
- View periodic tasks in Django admin
- Monitor task execution history
- Adjust schedule intervals

### Redis CLI Monitoring:
```bash
redis-cli monitor
```

## 🎛️ Production Tips

1. **Multiple Workers:** Run multiple worker processes for better performance
2. **Queue Separation:** Use different queues for different task priorities
3. **Monitoring:** Set up Flower for web-based monitoring
4. **Error Handling:** Tasks automatically retry on failure
5. **Resource Limits:** Configure memory and time limits per task

## 🔄 Migration from Management Command

The old `run_worker` management command is still available, but Celery provides:

- ✅ **Asynchronous processing** - No blocking
- ✅ **Auto-scaling** - Multiple workers  
- ✅ **Retry logic** - Failed task handling
- ✅ **Monitoring** - Task status tracking
- ✅ **Scheduling** - Periodic task execution
- ✅ **Distribution** - Multiple servers

## 🚨 Troubleshooting

**Redis Connection Issues:**
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

**Celery Import Errors:**
```bash
# Check if tasks are discovered
python manage.py shell
>>> from apps.worker.tasks import process_job
>>> process_job.delay(1)
```

**Task Not Executing:**
- Ensure Redis is running
- Check worker is consuming the correct queues
- Verify task routing configuration