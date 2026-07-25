# Page Pulse

Production-grade URL audit service built with FastAPI.

Page Pulse audits a target URL and returns useful response information such as HTTP status code, response time, content type, and content length.

The service is designed with production concerns in mind, including:

* Input validation
* Request timeouts
* Concurrency limits
* Configurable caching
* Per-client rate limiting
* Structured error responses
* Request IDs
* Structured logging
* Automated tests
* Continuous Integration with GitHub Actions

---

## Features

### URL Auditing

Submit a URL to the audit endpoint and receive:

* HTTP status code
* Response time in milliseconds
* Content type
* Content length
* Request ID
* Cache status

### Configurable Caching

Repeated audits of the same URL can be served from cache instead of refetching the target website.

The cache window can be configured using:

```env
CACHE_TTL_SECONDS=300
```

The default cache duration is **300 seconds (5 minutes)**.

### Rate Limiting

The service includes per-client rate limiting to prevent excessive requests.

Default configuration:

```text
60 requests per client
60-second time window
```

### Request Timeouts

External URL requests use configurable timeouts to prevent the service from waiting indefinitely for unresponsive websites.

### Concurrency Control

The service limits the number of simultaneous outbound requests to protect system resources.

### URL Validation

Incoming URLs are validated before processing.

The service prevents:

* Invalid URL formats
* Unsupported URL schemes
* Unsafe requests to private or local network addresses

### Structured Error Responses

Errors are returned using a consistent response format.

Example:

```json
{
  "error": {
    "code": "INVALID_URL",
    "message": "The provided URL is invalid."
  },
  "request_id": "example-request-id"
}
```

### Request IDs

Each request is assigned a unique request ID.

Request IDs help with:

* Debugging
* Log correlation
* Error tracking
* Production monitoring

### Structured Logging

The application uses structured logging to make application events easier to monitor and debug.

### Automated Testing

The project includes automated tests for:

* Health checks
* URL auditing
* URL validation
* Error handling
* Caching
* Rate limiting

### Continuous Integration

GitHub Actions automatically runs the test suite whenever code is pushed to the repository or a pull request is created.

---

## Technology Stack

* **Python 3.13**
* **FastAPI**
* **Uvicorn**
* **httpx**
* **Redis**
* **Pydantic**
* **Pytest**
* **GitHub Actions**

---

## Project Structure

```text
page-pulse/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── audits.py
│   │
│   ├── core/
│   │   └── logging.py
│   │
│   ├── exceptions/
│   │   └── fetch_exceptions.py
│   │
│   ├── schemas/
│   │   └── audit.py
│   │
│   ├── security/
│   │   └── url_validator.py
│   │
│   ├── services/
│   │   ├── cache_service.py
│   │   ├── fetch_service.py
│   │   └── rate_limit_service.py
│   │
│   ├── config.py
│   └── main.py
│
├── tests/
│   └── test_audits.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sundasZaib/page-pulse.git
cd page-pulse
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the project root if configuration values need to be customized.

Example:

```env
CACHE_TTL_SECONDS=300
REQUEST_TIMEOUT_SECONDS=10
MAX_CONCURRENT_REQUESTS=10
```

Configuration values may vary depending on the implementation and deployment environment.

---

## Running the Application

Start the development server using:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

### ReDoc

Open:

```text
http://127.0.0.1:8000/redoc
```

---

## Health Check

### Endpoint

```http
GET /health
```

### Example Response

```json
{
  "status": "healthy",
  "service": "page-pulse"
}
```

---

## URL Audit API

The audit endpoint accepts a target URL and returns information about the target website's HTTP response.

### Example Request

```http
POST /audits
```

Example request body:

```json
{
  "url": "https://example.com"
}
```

### Example Response

```json
{
  "url": "https://example.com",
  "status_code": 200,
  "response_time_ms": 245.32,
  "content_type": "text/html",
  "content_length": 1256,
  "cached": false,
  "request_id": "example-request-id"
}
```

The exact response fields may vary depending on the implementation.

---

## Running Tests

Run the complete test suite with:

```bash
pytest -q
```

Example:

```text
7 passed
```

The test suite is also executed automatically through GitHub Actions.

---

## Continuous Integration

The project includes a GitHub Actions workflow.

The CI pipeline:

1. Checks out the repository
2. Sets up Python
3. Installs project dependencies
4. Runs the automated tests

Workflow file:

```text
.github/workflows/ci.yml
```

---

## Caching

Page Pulse uses caching to avoid unnecessary repeated requests to the same URL.

When a URL is audited:

1. The service checks whether a valid cached result exists.
2. If a cached result exists, it is returned.
3. If no cached result exists, the target URL is fetched.
4. The result is stored in the cache.
5. Future requests can reuse the cached result until the cache expires.

This helps reduce:

* Network requests
* Response time
* External service load

---

## Rate Limiting

The service applies rate limiting on a per-client basis.

Default policy:

```text
Maximum requests: 60
Time window: 60 seconds
```

If a client exceeds the limit, the service rejects additional requests until the rate-limit window resets.

---

## Security Considerations

Page Pulse includes validation and protections for outbound URL requests.

Security considerations include:

* Validating incoming URLs
* Restricting unsupported URL schemes
* Preventing requests to unsafe private network destinations
* Applying request timeouts
* Limiting concurrent outbound requests
* Applying per-client rate limits

These protections help reduce the risk of:

* Server-Side Request Forgery (SSRF)
* Resource exhaustion
* Uncontrolled outbound requests

---

## Error Handling

The application uses structured error responses to provide predictable information to API consumers.

Common error categories may include:

* Invalid URL
* Unsupported URL scheme
* Request timeout
* Connection failure
* Rate limit exceeded
* Target server error

Errors include useful information for debugging while avoiding unnecessary internal implementation details.

---

## Design Goals

Page Pulse is designed around the following principles:

### Reliability

The service should handle slow, unavailable, or failing target websites gracefully.

### Security

User-provided URLs should be validated before the server makes outbound requests.

### Performance

Caching and concurrency control help reduce unnecessary work and improve response performance.

### Observability

Request IDs and structured logs make it easier to trace and debug requests.

### Maintainability

The codebase separates API routes, business logic, security validation, caching, rate limiting, and configuration into independent modules.

---

## Future Improvements

Potential future improvements include:

* Persistent Redis-based caching
* Distributed rate limiting
* Background audit jobs
* Historical audit results
* Scheduled monitoring
* Website uptime tracking
* Performance trend analysis
* Database-backed audit history
* Authentication and API keys
* Metrics and monitoring dashboards
* Docker containerization
* Production deployment configuration

---

## Development

The project follows a modular structure that separates responsibilities into different layers.

Main layers include:

* **API Layer** — Handles HTTP requests and responses.
* **Schema Layer** — Defines request and response data structures.
* **Service Layer** — Contains caching, fetching, and rate-limiting logic.
* **Security Layer** — Validates and protects outbound URL requests.
* **Core Layer** — Handles shared application functionality such as logging.
* **Exception Layer** — Defines application-specific errors.

---

## License

This project was created for educational and professional development purposes.

---

## Author

**Sundas Zaib**

Software Engineering Student | Python | FastAPI | Backend Development | AI & Machine Learning

GitHub: [@sundasZaib](https://github.com/sundasZaib)
