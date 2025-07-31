# Web Scraping Backend API Documentation

## Overview

This is a comprehensive Django REST Framework API for a web scraping platform that allows users to create projects, configure web spiders, manage scraping jobs, handle request/response queues, schedule automated runs, and manage sessions and proxies.

**Base URL**: `http://localhost:8000` (development)

**API Documentation**: Available at `/docs/` (Swagger UI) and `/redoc/` (ReDoc)

## Authentication

The API uses JWT (JSON Web Token) authentication with the following configuration:

- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 7 days
- **Header Format**: `Authorization: Bearer <access_token>`

### Authentication Endpoints

#### Register User
```http
POST /auth/register/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Login
```http
POST /auth/login/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Refresh Token
```http
POST /auth/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Logout
```http
POST /auth/logout/
```

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

## User Profile Management

### Get Current User Profile
```http
GET /profiles/me/
```

**Response (200):**
```json
{
  "id": 1,
  "display_name": "John Doe",
  "bio": "Web scraping enthusiast",
  "avatar": "/media/avatars/avatar.jpg",
  "user": {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Update Current User Profile
```http
PUT /profiles/me/
PATCH /profiles/me/
```

**Request Body:**
```json
{
  "display_name": "John Smith",
  "bio": "Updated bio",
  "user": {
    "first_name": "John",
    "last_name": "Smith"
  }
}
```

---

## Project Management

Projects are containers for organizing spiders and scraping activities.

### List Projects
```http
GET /projects/
```

**Response (200):**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "name": "E-commerce Scraper",
      "notes": "Scraping product data from various e-commerce sites",
      "created_at": "2024-01-15T10:30:00Z",
      "owner": 1
    }
  ]
}
```

### Create Project
```http
POST /projects/
```

**Request Body:**
```json
{
  "name": "News Scraper",
  "notes": "Scraping news articles from multiple sources"
}
```

### Get Project
```http
GET /projects/{id}/
```

### Update Project
```http
PUT /projects/{id}/
PATCH /projects/{id}/
```

### Delete Project
```http
DELETE /projects/{id}/
```

---

## Spider Management

Spiders define the web scraping configurations including start URLs, settings, and parsing rules.

### List Spiders
```http
GET /spiders/
```

**Response (200):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "project": 1,
      "name": "product-spider",
      "start_urls_json": [
        "https://example-shop.com/products",
        "https://example-shop.com/categories"
      ],
      "settings_json": {
        "timeout": 30,
        "user_agent": "Mozilla/5.0...",
        "headers": {
          "Accept": "text/html,application/xhtml+xml"
        }
      },
      "parse_rules_json": {
        "title": "css::h1.product-title::text",
        "price": "css::.price::text",
        "description": "xpath://div[@class='description']//text()"
      },
      "created_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

### Create Spider
```http
POST /spiders/
```

**Request Body:**
```json
{
  "project": 1,
  "name": "product-spider",
  "start_urls_json": [
    "https://example-shop.com/products"
  ],
  "settings_json": {
    "timeout": 30,
    "concurrent_requests": 16,
    "download_delay": 1
  },
  "parse_rules_json": {
    "title": "css::h1.product-title::text",
    "price": "css::.price::text"
  }
}
```

### Get/Update/Delete Spider
```http
GET /spiders/{id}/
PUT /spiders/{id}/
PATCH /spiders/{id}/
DELETE /spiders/{id}/
```

---

## Job Management

Jobs represent individual execution instances of spiders.

### List Jobs
```http
GET /jobs/
```

**Response (200):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "spider": 1,
      "status": "done",
      "started_at": "2024-01-15T12:00:00Z",
      "finished_at": "2024-01-15T12:05:30Z",
      "stats_json": {
        "requests_count": 150,
        "responses_count": 148,
        "items_scraped": 75,
        "errors_count": 2
      },
      "created_at": "2024-01-15T11:59:50Z",
      "duration": 330.0
    }
  ]
}
```

### Create Job
```http
POST /jobs/
```

**Request Body:**
```json
{
  "spider": 1
}
```

**Job Status Values:**
- `queued`: Job is waiting to be processed
- `running`: Job is currently executing
- `done`: Job completed successfully
- `failed`: Job failed with errors
- `canceled`: Job was canceled

### Get/Update/Delete Job
```http
GET /jobs/{id}/
PUT /jobs/{id}/
PATCH /jobs/{id}/
DELETE /jobs/{id}/
```

---

## Request Queue Management

The request queue manages HTTP requests to be processed during spider execution.

### List Requests
```http
GET /requests/
```

**Response (200):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "job": 1,
      "url": "https://example.com/page1",
      "method": "GET",
      "headers_json": {
        "User-Agent": "Mozilla/5.0...",
        "Accept": "text/html"
      },
      "body_blob": null,
      "priority": 0,
      "depth": 0,
      "retries": 0,
      "max_retries": 3,
      "fingerprint": "a1b2c3d4e5f6...",
      "scheduled_at": "2024-01-15T12:00:00Z",
      "picked_at": "2024-01-15T12:00:05Z",
      "status": "done",
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:00:10Z",
      "can_retry": true
    }
  ]
}
```

### Create Request
```http
POST /requests/
```

**Request Body:**
```json
{
  "job": 1,
  "url": "https://example.com/api/data",
  "method": "POST",
  "headers_json": {
    "Content-Type": "application/json"
  },
  "body_blob": "eyJrZXkiOiJ2YWx1ZSJ9",  // base64 encoded
  "priority": 10,
  "depth": 1,
  "max_retries": 5
}
```

**Request Status Values:**
- `pending`: Request is waiting to be processed
- `in_progress`: Request is currently being processed
- `done`: Request completed successfully
- `error`: Request failed
- `skipped`: Request was skipped

**HTTP Methods Supported:**
- GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS

### Get/Update/Delete Request
```http
GET /requests/{id}/
PUT /requests/{id}/
PATCH /requests/{id}/
DELETE /requests/{id}/
```

---

## Response Management

Responses store the results of processed HTTP requests, including status codes, headers, and body content.

### List Responses
```http
GET /responses/
```

**Response (200):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "request": 1,
      "final_url": "https://example.com/page1",
      "status_code": 200,
      "headers_json": {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Length": "15420"
      },
      "fetched_at": "2024-01-15T12:00:10Z",
      "latency_ms": 450,
      "from_cache": false,
      "body_path": "responses/2024/01/15/response_1_120010.html",
      "content_hash": "sha256:a1b2c3d4...",
      "created_at": "2024-01-15T12:00:10Z",
      "updated_at": "2024-01-15T12:00:10Z",
      "is_success": true,
      "is_redirect": false,
      "is_client_error": false,
      "is_server_error": false,
      "body_size": 15420
    }
  ]
}
```

### Create Response
```http
POST /responses/
```

**Request Body:**
```json
{
  "request": 1,
  "final_url": "https://example.com/page1",
  "status_code": 200,
  "headers_json": {
    "Content-Type": "text/html"
  },
  "latency_ms": 450,
  "from_cache": false
}
```

### Get/Update/Delete Response
```http
GET /responses/{id}/
PUT /responses/{id}/
PATCH /responses/{id}/
DELETE /responses/{id}/
```

**Note**: Response bodies are stored as files on disk. The `body_path` field contains the relative path to the stored file. Bodies are automatically organized by date in the directory structure: `media/responses/YYYY/MM/DD/`.

---

## Schedule Management

Schedules allow automatic execution of spiders using cron expressions.

### List Schedules
```http
GET /schedules/
```

**Response (200):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "spider": 1,
      "cron_expr": "0 */6 * * *",
      "timezone": "Australia/Brisbane",
      "enabled": true,
      "next_run_at": "2024-01-15T18:00:00Z",
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:00:00Z",
      "time_until_next_run": "6:00:00",
      "is_overdue": false,
      "is_due": false
    }
  ]
}
```

### Create Schedule
```http
POST /schedules/
```

**Request Body:**
```json
{
  "spider": 1,
  "cron_expr": "0 */6 * * *",
  "timezone": "UTC",
  "enabled": true
}
```

**Cron Expression Format:**
```
minute hour day month weekday
*      *    *   *     *
```

**Cron Field Ranges:**
- minute: 0-59
- hour: 0-23
- day: 1-31
- month: 1-12
- weekday: 0-7 (0 and 7 are Sunday)

**Common Cron Examples:**
- `0 */6 * * *` - Every 6 hours
- `0 9 * * 1-5` - Every weekday at 9 AM
- `*/15 * * * *` - Every 15 minutes
- `0 0 1 * *` - First day of every month at midnight

### Get/Update/Delete Schedule
```http
GET /schedules/{id}/
PUT /schedules/{id}/
PATCH /schedules/{id}/
DELETE /schedules/{id}/
```

---

## Session Management

Sessions store authentication state (cookies, headers) for spiders that need to maintain logged-in states.

### List Sessions
```http
GET /sessions/
```

**Response (200):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "spider": 1,
      "spider_name": "product-spider",
      "label": "user123_session",
      "cookies_json": {
        "session_id": "abc123def456",
        "csrf_token": "xyz789"
      },
      "headers_json": {
        "X-Requested-With": "XMLHttpRequest"
      },
      "valid_until": "2024-01-16T12:00:00Z",
      "is_expired": false,
      "is_valid": true,
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

### Create Session
```http
POST /sessions/
```

**Request Body:**
```json
{
  "spider": 1,
  "label": "admin_session",
  "cookies_json": {
    "sessionid": "abc123",
    "csrftoken": "def456"
  },
  "headers_json": {
    "X-CSRFToken": "def456"
  },
  "valid_until": "2024-01-16T12:00:00Z"
}
```

### Extend Session Validity
```http
POST /sessions/{id}/extend_validity/
```

**Request Body:**
```json
{
  "hours": 48
}
```

### Get/Update/Delete Session
```http
GET /sessions/{id}/
PUT /sessions/{id}/
PATCH /sessions/{id}/
DELETE /sessions/{id}/
```

---

## Proxy Management

Proxies enable rotating IP addresses and avoiding rate limits during scraping.

### List Proxies
```http
GET /proxies/
```

**Response (200):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "uri": "http://username:password@proxy.example.com:8080",
      "masked_uri": "http://username:***@proxy.example.com:8080",
      "hostname": "proxy.example.com",
      "port": 8080,
      "scheme": "http",
      "is_active": true,
      "last_ok_at": "2024-01-15T11:30:00Z",
      "fail_count": 0,
      "is_healthy": true,
      "success_rate": 95.5,
      "meta_json": {
        "total_attempts": 100,
        "successful_attempts": 95,
        "last_success_at": "2024-01-15T11:30:00Z"
      },
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T11:30:00Z"
    }
  ]
}
```

### Create Proxy
```http
POST /proxies/
```

**Request Body:**
```json
{
  "uri": "http://username:password@proxy.example.com:8080",
  "is_active": true,
  "meta_json": {
    "location": "US",
    "provider": "ProxyProvider Inc"
  }
}
```

**Supported Proxy Schemes:**
- `http://` - HTTP proxy
- `https://` - HTTPS proxy  
- `socks4://` - SOCKS4 proxy
- `socks5://` - SOCKS5 proxy

### Mark Proxy Success
```http
POST /proxies/{id}/mark_success/
```

### Mark Proxy Failure
```http
POST /proxies/{id}/mark_failure/
```

**Request Body:**
```json
{
  "error_message": "Connection timeout after 30 seconds"
}
```

### Reset Proxy Stats
```http
POST /proxies/{id}/reset_stats/
```

### Get/Update/Delete Proxy
```http
GET /proxies/{id}/
PUT /proxies/{id}/
PATCH /proxies/{id}/
DELETE /proxies/{id}/
```

---

## Data Relationships

The API follows a hierarchical structure:

```
User
└── Projects
    └── Spiders
        ├── Jobs
        │   ├── Requests
        │   │   └── Responses
        │   └── Stats
        ├── Schedules
        └── Sessions

Proxies (Global, not tied to specific spiders)
```

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "field_name": ["Error message for this field"],
  "non_field_errors": ["General error messages"]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

## Pagination

List endpoints support pagination with the following parameters:

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Response Format:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/projects/?page=3",
  "previous": "http://localhost:8000/projects/?page=1",
  "results": [...]
}
```

## Filtering and Ordering

Many endpoints support filtering and ordering:

**Examples:**
```http
GET /jobs/?status=running&spider=1
GET /responses/?status_code=200&ordering=-fetched_at
GET /schedules/?enabled=true&ordering=next_run_at
```

## File Uploads

- **Profile avatars**: Upload to `/profiles/me/` with `multipart/form-data`
- **Response bodies**: Automatically stored by the system in `media/responses/YYYY/MM/DD/`

## CORS Configuration

The API supports CORS for frontend development with these allowed origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:8080`
- `http://127.0.0.1:8080`

## Rate Limiting

The API uses JWT token expiration for rate limiting:
- Access tokens expire after 60 minutes
- Refresh tokens expire after 7 days

## Development Notes

- **Database**: SQLite (development), easily configurable for PostgreSQL/MySQL in production
- **Media Files**: Stored in `media/` directory during development
- **API Documentation**: Available at `/docs/` (Swagger) and `/redoc/` 
- **Admin Interface**: Available at `/admin/` for backend management

This API provides a complete foundation for building a web scraping frontend application with user management, project organization, spider configuration, job execution monitoring, scheduling capabilities, and proxy rotation support.