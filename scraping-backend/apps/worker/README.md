# Web Scraping Worker

The worker app is a separate process that processes queued scraping jobs using Playwright. It automatically processes the oldest jobs in the queue and handles all aspects of web scraping including request logging and response storage.

## Features

- **Automatic Job Processing**: Processes jobs with 'queued' status in chronological order
- **Playwright Integration**: Uses Playwright for robust web scraping with browser automation
- **Request/Response Logging**: Automatically logs requests and stores responses
- **Error Handling**: Comprehensive error handling with retry mechanisms
- **Configurable**: Support for different browsers, headless/headed mode, timeouts, etc.

## How It Works

1. **Job Selection**: The worker continuously monitors the job queue and picks up the oldest job with status 'queued'
2. **Job Processing**: For each job, it:
   - Updates job status to 'running'
   - Processes all start URLs from the spider configuration
   - Creates request records for each URL
   - Uses Playwright to navigate to URLs
   - Captures responses and stores them
   - Handles any additional requests in the queue
3. **Completion**: Marks the job as 'done' or 'failed' based on the outcome

## Usage

### Install Dependencies

First, install Playwright and its browser dependencies:

```bash
pip install -r requirements.txt
playwright install
```

### Run the Worker

Use the Django management command to start the worker:

```bash
# Basic usage
python manage.py run_worker

# With options
python manage.py run_worker --browser chromium --headless --concurrent-jobs 1 --job-timeout 300

# Run in headed mode for debugging
python manage.py run_worker --headed

# Use Firefox browser
python manage.py run_worker --browser firefox

# Increase verbosity
python manage.py run_worker --log-level DEBUG
```

### Command Options

- `--browser`: Browser type ('chromium', 'firefox', 'webkit') - default: chromium
- `--headless`: Run in headless mode (default: True)
- `--headed`: Run in headed mode (opposite of --headless)
- `--concurrent-jobs`: Number of jobs to process concurrently - default: 1
- `--job-timeout`: Timeout for each job in seconds - default: 300
- `--log-level`: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') - default: INFO

## Architecture

### Components

1. **WorkerService**: Main service class that handles job processing
2. **WorkerManager**: Manager class for running the service
3. **RequestAPIClient**: Client for managing request queue operations
4. **ResponseAPIClient**: Client for managing response operations

### Data Flow

```
Job (queued) → Worker picks up → Creates requests → Uses Playwright → Stores responses → Job (done)
```

### Integration Points

- **Job Model**: Reads jobs with 'queued' status
- **Spider Model**: Uses start_urls_json for initial requests
- **RequestQueue Model**: Creates and manages request records
- **Response Model**: Stores all response data and content

## Configuration

The worker can be configured through command-line options or by modifying the `WorkerService` class initialization parameters.

### Default Settings

- Browser: Chromium
- Mode: Headless
- Concurrent Jobs: 1
- Job Timeout: 300 seconds
- Page Timeout: 30 seconds
- Network Idle Timeout: 10 seconds

## Monitoring

The worker logs all activities to both stdout and `worker.log` file. Monitor the logs for:

- Job processing status
- Request/response details
- Error messages
- Performance metrics

## Error Handling

The worker includes comprehensive error handling:

- **Job Level**: Failed jobs are marked with 'failed' status
- **Request Level**: Failed requests are logged with error responses
- **Network Level**: Timeouts and connection errors are handled gracefully
- **Browser Level**: Browser crashes are handled with cleanup

## Development

### Running for Development

For development, run the worker in headed mode to see browser interactions:

```bash
python manage.py run_worker --headed --log-level DEBUG
```

### Testing

The worker integrates with existing models, so test by:

1. Creating a spider with start URLs
2. Creating a job for that spider
3. Running the worker
4. Checking request and response records

## Production Deployment

For production deployment:

1. Install all dependencies including Playwright browsers
2. Run as a background service
3. Set up log rotation for `worker.log`
4. Monitor process health
5. Consider running multiple worker instances for scalability

```bash
# Example systemd service
# Save as /etc/systemd/system/scraping-worker.service
[Unit]
Description=Web Scraping Worker
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/python manage.py run_worker
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```