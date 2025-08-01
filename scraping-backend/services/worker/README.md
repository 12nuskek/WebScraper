# Basic Web Scraping Worker

A simple, standalone worker that processes web scraping jobs from the database without requiring Redis or Celery.

## Overview

This worker:
- Polls the database for jobs with status 'queued'
- Processes jobs by displaying all job and related record information as JSON
- Updates job status and statistics
- Runs independently in the same virtual environment as the Django app

## Files

- `basic_worker.py` - Main worker implementation
- `run_worker.py` - Command-line interface for the worker
- `start_worker.sh` - Shell script to start the worker with virtual environment
- `README.md` - This documentation

## How It Works

1. **Job Discovery**: The worker queries the `job_job` table for records with `status='queued'`, ordered by `created_at` (oldest first)

2. **Job Processing**: 
   - Updates job status to 'running' 
   - Sets `started_at` timestamp
   - Retrieves spider configuration (URLs, settings, parse rules)
   - Displays all job and related record information as formatted JSON
   - Saves the job data as a JSON file in the media directory
   - Updates job status to 'done' or 'failed'
   - Sets `finished_at` timestamp and statistics

3. **Polling Loop**: Continuously checks for new jobs every N seconds (default: 5)

## Usage

### Method 1: Using the shell script (recommended)
```bash
cd scraping-backend/services/worker
chmod +x start_worker.sh
./start_worker.sh
```

### Method 2: Using Python directly
```bash
cd scraping-backend
python services/worker/run_worker.py
```

### Method 3: With custom poll interval
```bash
# Check for jobs every 10 seconds instead of 5
python services/worker/run_worker.py --poll-interval 10
```

## Configuration

The worker uses the same Django settings as the main application (`config.settings.local`).

### Spider Configuration

Spiders are configured in the database with JSON fields:

- `start_urls_json`: Array of URLs to scrape
- `settings_json`: HTTP settings (timeout, headers, etc.)
- `parse_rules_json`: Data extraction rules (placeholder for future expansion)

Example spider settings:
```json
{
  "timeout": 30,
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  }
}
```

## Job Status Flow

```
queued → running → done/failed
```

- `queued`: Job is waiting to be processed
- `running`: Worker is currently processing the job
- `done`: Job completed successfully
- `failed`: Job encountered an error

## JSON File Output

Each processed job generates a JSON file saved to:
- Location: `media/job_results/`
- Filename format: `job_{job_id}_{timestamp}.json`
- Contains:
  - Metadata (export timestamp, worker version, job ID)
  - Complete job information (job, spider, project, owner data)

Example file structure:
```json
{
  "metadata": {
    "exported_at": "2025-01-15T10:30:00Z",
    "worker_version": "1.0",
    "file_format": "json",
    "job_id": 8
  },
  "data": {
    "job": { ... },
    "spider": { ... },
    "project": { ... },
    "owner": { ... }
  }
}
```

## Logging

The worker logs to:
- Console (stdout)
- `worker.log` file in the current directory

Log levels:
- INFO: Job processing updates, JSON file saves
- WARNING: Non-fatal errors (e.g., failed to scrape a single URL)
- ERROR: Fatal job failures, JSON save failures

## Dependencies

- Django (from main application)
- No additional dependencies required for JSON display mode

## Stopping the Worker

Press `Ctrl+C` to gracefully stop the worker. It will finish processing the current job before shutting down.

## Extending the Worker

### Adding More Sophisticated Parsing

Modify the `extract_data()` method in `basic_worker.py` to add:
- BeautifulSoup for HTML parsing
- CSS selector or XPath support
- Data validation and cleaning
- Custom extraction pipelines

### Adding Data Storage

The current implementation stores basic statistics in the job record. You can extend this to:
- Save scraped data to separate tables
- Export data to files
- Send data to external APIs

### Error Handling

Add more robust error handling for:
- Network timeouts
- Rate limiting
- Proxy rotation
- Retry logic

## Example Job Creation

To test the worker, create a job through the Django admin or API:

```python
from apps.spider.models import Spider
from apps.job.models import Job

# Assuming you have a spider configured
spider = Spider.objects.first()
job = Job.objects.create(spider=spider, status='queued')
```

The worker will pick up this job on its next polling cycle.