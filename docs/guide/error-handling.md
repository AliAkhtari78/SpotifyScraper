# Error Handling Guide

This guide covers how to handle errors gracefully when using SpotifyScraper and implement robust error recovery.

## Table of Contents
- [Overview](#overview)
- [Common Errors](#common-errors)
- [Exception Types](#exception-types)
- [Error Handling Patterns](#error-handling-patterns)
- [Retry Strategies](#retry-strategies)
- [Logging and Debugging](#logging-and-debugging)
- [Production Error Handling](#production-error-handling)
- [Best Practices](#best-practices)

---

## Overview

SpotifyScraper provides comprehensive error handling to help you build robust applications. Understanding error types and implementing proper error handling is crucial for production use.

### Error Categories

- **Network Errors**: Connection issues, timeouts, DNS failures
- **Authentication Errors**: Invalid cookies, expired sessions
- **Data Errors**: Invalid URLs, missing content, parsing failures
- **Rate Limiting**: Too many requests, temporary blocks
- **System Errors**: File system issues, permission problems

### Error Handling Philosophy

- **Fail Fast**: Detect errors early and provide clear feedback
- **Graceful Degradation**: Continue working when possible
- **Detailed Logging**: Provide actionable error information
- **Recovery Strategies**: Automatic retry with backoff

---

## Common Errors

### Network-Related Errors

#### Connection Timeout
```python
from spotify_scraper import SpotifyClient
from spotify_scraper import TimeoutError

client = SpotifyClient(timeout=30)

try:
    track = client.get_track_info(url)
except TimeoutError as e:
    print(f"Request timed out: {e}")
    # Handle timeout - maybe retry with longer timeout
```

#### Connection Failed
```python
from spotify_scraper import ConnectionError

try:
    track = client.get_track_info(url)
except ConnectionError as e:
    print(f"Connection failed: {e}")
    # Check internet connection or try different proxy
```

#### Rate Limiting
```python
from spotify_scraper import RateLimitError
import time

try:
    track = client.get_track_info(url)
except RateLimitError as e:
    print(f"Rate limited: {e}")
    wait_time = e.retry_after or 60  # Wait time in seconds
    print(f"Waiting {wait_time} seconds before retry...")
    time.sleep(wait_time)
    # Retry the request
```

### Data-Related Errors

#### Invalid URL
```python
from spotify_scraper import InvalidURLError

try:
    track = client.get_track_info("invalid-url")
except InvalidURLError as e:
    print(f"Invalid Spotify URL: {e}")
    # Validate URL format before processing
```

#### Content Not Found
```python
from spotify_scraper import NotFoundError

try:
    track = client.get_track_info("https://open.spotify.com/track/nonexistent")
except NotFoundError as e:
    print(f"Track not found: {e}")
    # Handle missing content gracefully
```

#### Parsing Errors
```python
from spotify_scraper import ParseError

try:
    track = client.get_track_info(url)
except ParseError as e:
    print(f"Failed to parse response: {e}")
    # Log the error for investigation
```

### Authentication Errors

#### Invalid Cookies
```python
from spotify_scraper import AuthenticationError

try:
    client = SpotifyClient(cookies={'sp_dc': 'invalid_cookie'})
    track = client.get_track_info(url)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Refresh cookies or switch to unauthenticated mode
```

---

## Exception Types

SpotifyScraper provides a comprehensive exception hierarchy:

### Base Exception
```python
from spotify_scraper import SpotifyScraperError

# Catch all SpotifyScraper-specific errors
try:
    result = client.get_track_info(url)
except SpotifyScraperError as e:
    print(f"SpotifyScraper error: {e}")
```

### Network Exceptions
```python
from spotify_scraper import (
    NetworkError,      # Base network error
    ConnectionError,   # Connection failed
    TimeoutError,      # Request timeout
    DNSError,         # DNS resolution failed
    SSLError          # SSL/TLS errors
)

def handle_network_errors(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ConnectionError:
        print("Connection failed - check internet connection")
    except TimeoutError:
        print("Request timed out - try increasing timeout")
    except DNSError:
        print("DNS resolution failed - check domain name")
    except SSLError:
        print("SSL error - check certificate or disable SSL verification")
    except NetworkError as e:
        print(f"Network error: {e}")
```

### HTTP Exceptions
```python
from spotify_scraper import (
    HTTPError,         # Base HTTP error
    BadRequestError,   # 400 Bad Request
    UnauthorizedError, # 401 Unauthorized
    ForbiddenError,    # 403 Forbidden
    NotFoundError,     # 404 Not Found
    TooManyRequestsError, # 429 Too Many Requests
    ServerError        # 5xx Server errors
)

def handle_http_errors(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except BadRequestError:
        print("Bad request - check URL format")
    except UnauthorizedError:
        print("Unauthorized - check authentication")
    except ForbiddenError:
        print("Forbidden - access denied")
    except NotFoundError:
        print("Content not found")
    except TooManyRequestsError as e:
        print(f"Rate limited - retry after {e.retry_after} seconds")
    except ServerError:
        print("Server error - try again later")
```

### Data Exceptions
```python
from spotify_scraper import (
    DataError,         # Base data error
    InvalidURLError,   # Invalid Spotify URL
    ParseError,        # Failed to parse response
    ValidationError,   # Data validation failed
    MissingDataError   # Required data missing
)

def handle_data_errors(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except InvalidURLError as e:
        print(f"Invalid URL: {e}")
        return None
    except ParseError as e:
        print(f"Parse error: {e}")
        # Log for debugging
    except ValidationError as e:
        print(f"Validation error: {e}")
    except MissingDataError as e:
        print(f"Missing data: {e}")
```

---

## Error Handling Patterns

### Basic Try-Catch Pattern

```python
def safe_get_track(client, url):
    """Safely get track info with basic error handling."""
    try:
        return client.get_track_info(url)
    except Exception as e:
        print(f"Failed to get track info: {e}")
        return None

# Usage
track = safe_get_track(client, url)
if track:
    print(f"Track: {track.get('name', 'Unknown')}")
else:
    print("Failed to get track info")
```

### Specific Exception Handling

```python
from spotify_scraper import (
    TimeoutError, RateLimitError, NotFoundError
)

def robust_get_track(client, url):
    """Get track info with specific error handling."""
    try:
        return client.get_track_info(url)
        
    except TimeoutError:
        print("Request timed out - the server might be slow")
        return None
        
    except RateLimitError as e:
        print(f"Rate limited - wait {e.retry_after} seconds")
        return None
        
    except NotFoundError:
        print("Track not found - URL might be invalid")
        return None
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Context Manager Pattern

```python
from contextlib import contextmanager

@contextmanager
def spotify_client_context(**kwargs):
    """Context manager for SpotifyClient with error handling."""
    client = None
    try:
        client = SpotifyClient(**kwargs)
        yield client
    except Exception as e:
        print(f"Client error: {e}")
        raise
    finally:
        if client:
            try:
                client.close()
            except Exception as e:
                print(f"Error closing client: {e}")

# Usage
try:
    with spotify_client_context() as client:
        track = client.get_track_info(url)
        print(f"Track: {track.get('name', 'Unknown')}")
except Exception as e:
    print(f"Operation failed: {e}")
```

### Decorator Pattern

```python
import functools
import logging

def handle_spotify_errors(func):
    """Decorator to handle SpotifyScraper errors."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            logging.warning(f"Rate limited in {func.__name__}: {e}")
            return None
        except TimeoutError as e:
            logging.warning(f"Timeout in {func.__name__}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

@handle_spotify_errors
def get_track_safely(client, url):
    return client.get_track_info(url)

# Usage
track = get_track_safely(client, url)
```

---

## Retry Strategies

### Simple Retry

```python
import time
import random

def retry_on_error(func, *args, max_retries=3, delay=1, **kwargs):
    """Retry function on error with exponential backoff."""
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
            
        except (TimeoutError, ConnectionError, ServerError) as e:
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                print(f"All {max_retries} attempts failed")
                raise
        
        except Exception as e:
            # Don't retry on non-recoverable errors
            print(f"Non-recoverable error: {e}")
            raise

# Usage
track = retry_on_error(client.get_track_info, url, max_retries=3)
```

### Advanced Retry with Backoff

```python
import time
import random
from datetime import datetime, timedelta

class RetryHandler:
    def __init__(self, max_retries=3, base_delay=1, max_delay=60):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_count = {}
    
    def should_retry(self, exception):
        """Determine if error should trigger retry."""
        retryable_errors = (
            TimeoutError,
            ConnectionError,
            ServerError,
            RateLimitError
        )
        return isinstance(exception, retryable_errors)
    
    def get_delay(self, attempt, exception=None):
        """Calculate delay for retry attempt."""
        if isinstance(exception, RateLimitError) and exception.retry_after:
            return min(exception.retry_after, self.max_delay)
        
        # Exponential backoff with jitter
        delay = self.base_delay * (2 ** attempt)
        jitter = random.uniform(0, delay * 0.1)
        return min(delay + jitter, self.max_delay)
    
    def execute(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if not self.should_retry(e):
                    print(f"Non-retryable error: {e}")
                    raise
                
                if attempt < self.max_retries - 1:
                    delay = self.get_delay(attempt, e)
                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    print(f"All {self.max_retries} attempts failed")
                    raise last_exception

# Usage
retry_handler = RetryHandler(max_retries=5, base_delay=2)
track = retry_handler.execute(client.get_track_info, url)
```

### Rate Limit Aware Retry

```python
class RateLimitAwareRetry:
    def __init__(self, requests_per_minute=30):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    def wait_if_needed(self):
        """Wait if we're approaching rate limit."""
        now = datetime.now()
        
        # Remove requests older than 1 minute
        self.request_times = [
            t for t in self.request_times 
            if now - t < timedelta(minutes=1)
        ]
        
        # If we're at the limit, wait
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0]).total_seconds()
            if sleep_time > 0:
                print(f"Rate limit reached. Waiting {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
                self.request_times = []  # Reset after waiting
    
    def execute(self, func, *args, **kwargs):
        """Execute function with rate limiting."""
        self.wait_if_needed()
        
        try:
            result = func(*args, **kwargs)
            self.request_times.append(datetime.now())
            return result
            
        except RateLimitError as e:
            print(f"Rate limited despite precautions: {e}")
            wait_time = e.retry_after or 60
            time.sleep(wait_time)
            self.request_times = []  # Reset after rate limit
            raise  # Re-raise to trigger retry

# Usage
rate_limiter = RateLimitAwareRetry(requests_per_minute=20)
retry_handler = RetryHandler()

def safe_get_track(url):
    return rate_limiter.execute(client.get_track_info, url)

track = retry_handler.execute(safe_get_track, url)
```

---

## Logging and Debugging

### Configure Logging

```python
import logging
from spotify_scraper import SpotifyClient

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spotify_scraper.log'),
        logging.StreamHandler()
    ]
)

# Create logger for your application
logger = logging.getLogger('my_spotify_app')

# Create client with debug logging
client = SpotifyClient(log_level="DEBUG")
```

### Error Logging Best Practices

```python
import logging
import traceback
from datetime import datetime

class ErrorLogger:
    def __init__(self, logger_name='spotify_errors'):
        self.logger = logging.getLogger(logger_name)
        
        # Configure error-specific handler
        error_handler = logging.FileHandler('errors.log')
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
    
    def log_error(self, operation, url, error, context=None):
        """Log error with context."""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'url': url,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        # Log error details
        self.logger.error(f"Operation failed: {operation}")
        self.logger.error(f"URL: {url}")
        self.logger.error(f"Error: {error}")
        
        if context:
            self.logger.error(f"Context: {context}")
        
        # Log full traceback for debugging
        self.logger.debug(traceback.format_exc())
        
        return error_info

# Usage
error_logger = ErrorLogger()

def get_track_with_logging(client, url):
    try:
        return client.get_track_info(url)
    except Exception as e:
        error_logger.log_error(
            operation='get_track_info',
            url=url,
            error=e,
            context={
                'client_config': client.config,
                'attempt_time': datetime.now().isoformat()
            }
        )
        raise
```

### Debug Mode

```python
def debug_spotify_operation(client, operation, *args, **kwargs):
    """Execute operation with detailed debugging."""
    
    print(f"=== DEBUG: {operation.__name__} ===")
    print(f"Args: {args}")
    print(f"Kwargs: {kwargs}")
    print(f"Client config: {client.config}")
    
    try:
        start_time = time.time()
        result = operation(*args, **kwargs)
        end_time = time.time()
        
        print(f"✅ Success in {end_time - start_time:.2f}s")
        print(f"Result type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"Result keys: {list(result.keys())}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        print(f"Traceback:")
        traceback.print_exc()
        raise

# Usage in debug mode
if DEBUG:
    track = debug_spotify_operation(client, client.get_track_info, url)
else:
    track = client.get_track_info(url)
```

---

## Production Error Handling

### Comprehensive Error Handler

```python
import logging
import sys
from typing import Optional, Any, Callable
from dataclasses import dataclass

@dataclass
class ErrorResult:
    success: bool
    result: Optional[Any] = None
    error: Optional[Exception] = None
    error_type: Optional[str] = None
    retry_after: Optional[int] = None

class ProductionErrorHandler:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts = {}
        
    def handle_operation(
        self, 
        operation: Callable,
        *args,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        circuit_breaker_threshold: int = 10,
        **kwargs
    ) -> ErrorResult:
        """Handle operation with comprehensive error handling."""
        
        operation_name = operation.__name__
        
        # Check circuit breaker
        if self._is_circuit_broken(operation_name, circuit_breaker_threshold):
            return ErrorResult(
                success=False,
                error_type="circuit_breaker",
                error=Exception(f"Circuit breaker open for {operation_name}")
            )
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = operation(*args, **kwargs)
                
                # Reset error count on success
                self.error_counts[operation_name] = 0
                
                return ErrorResult(success=True, result=result)
                
            except RateLimitError as e:
                self.logger.warning(f"Rate limited: {e}")
                return ErrorResult(
                    success=False,
                    error=e,
                    error_type="rate_limit",
                    retry_after=e.retry_after
                )
                
            except (TimeoutError, ConnectionError) as e:
                last_error = e
                self._increment_error_count(operation_name)
                
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Non-retryable error in {operation_name}: {e}")
                self._increment_error_count(operation_name)
                
                return ErrorResult(
                    success=False,
                    error=e,
                    error_type=type(e).__name__
                )
        
        # All retries failed
        self.logger.error(f"All retries failed for {operation_name}")
        return ErrorResult(
            success=False,
            error=last_error,
            error_type="max_retries_exceeded"
        )
    
    def _increment_error_count(self, operation_name: str):
        """Increment error count for circuit breaker."""
        self.error_counts[operation_name] = self.error_counts.get(operation_name, 0) + 1
    
    def _is_circuit_broken(self, operation_name: str, threshold: int) -> bool:
        """Check if circuit breaker should be open."""
        return self.error_counts.get(operation_name, 0) >= threshold

# Usage
error_handler = ProductionErrorHandler()

def get_track_production(client, url):
    """Production-ready track extraction."""
    
    result = error_handler.handle_operation(
        client.get_track_info,
        url,
        max_retries=3,
        retry_delay=2.0
    )
    
    if result.success:
        return result.result
    else:
        if result.error_type == "rate_limit":
            # Handle rate limiting
            print(f"Rate limited. Retry after {result.retry_after} seconds")
        elif result.error_type == "circuit_breaker":
            # Handle circuit breaker
            print("Service temporarily unavailable")
        else:
            # Handle other errors
            print(f"Error: {result.error}")
        
        return None
```

### Error Reporting and Monitoring

```python
import json
from datetime import datetime
from pathlib import Path

class ErrorReporter:
    def __init__(self, report_file="error_report.json"):
        self.report_file = Path(report_file)
        self.errors = []
    
    def report_error(self, operation, url, error, context=None):
        """Report error for monitoring."""
        
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'url': url,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self.errors.append(error_record)
        self._save_report()
        
        # Alert if error rate is high
        self._check_error_rate()
    
    def _save_report(self):
        """Save error report to file."""
        with open(self.report_file, 'w') as f:
            json.dump(self.errors, f, indent=2)
    
    def _check_error_rate(self):
        """Check if error rate is concerning."""
        recent_errors = [
            e for e in self.errors[-100:]  # Last 100 operations
            if datetime.fromisoformat(e['timestamp']) > 
               datetime.now().replace(hour=0, minute=0, second=0)  # Today
        ]
        
        if len(recent_errors) > 10:  # More than 10 errors today
            print("⚠️ High error rate detected!")
            self._send_alert(recent_errors)
    
    def _send_alert(self, recent_errors):
        """Send alert about high error rate."""
        # Implement your alerting logic here
        # Could send email, Slack message, etc.
        pass

# Integration with error handling
error_reporter = ErrorReporter()

def monitored_operation(client, operation_name, operation_func, *args, **kwargs):
    """Execute operation with monitoring."""
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        error_reporter.report_error(
            operation=operation_name,
            url=args[0] if args else "unknown",
            error=e,
            context={
                'args': str(args),
                'kwargs': str(kwargs)
            }
        )
        raise
```

---

## Best Practices

### 1. Error Hierarchy

```python
# Handle errors from specific to general
try:
    track = client.get_track_info(url)
except NotFoundError:
    # Handle specific case
    return handle_missing_track(url)
except RateLimitError as e:
    # Handle rate limiting
    return handle_rate_limit(e)
except NetworkError:
    # Handle network issues
    return handle_network_error()
except SpotifyScraperError:
    # Handle any SpotifyScraper error
    return handle_general_error()
except Exception:
    # Handle unexpected errors
    return handle_unexpected_error()
```

### 2. Graceful Degradation

```python
def get_track_with_fallback(client, url):
    """Get track info with graceful degradation."""
    
    try:
        # Try full track info
        return client.get_track_info(url)
        
    except NotFoundError:
        # Track not found - return None
        return None
        
    except RateLimitError:
        # Rate limited - try basic info only
        try:
            return client.get_basic_track_info(url)
        except Exception:
            return None
            
    except Exception as e:
        # Other errors - log and return None
        logging.error(f"Failed to get track info: {e}")
        return None
```

### 3. Resource Cleanup

```python
class SafeSpotifyClient:
    def __init__(self, **kwargs):
        self.client = None
        self._init_client(**kwargs)
    
    def _init_client(self, **kwargs):
        """Initialize client with error handling."""
        try:
            self.client = SpotifyClient(**kwargs)
        except Exception as e:
            logging.error(f"Failed to initialize client: {e}")
            raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Safely close client."""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logging.warning(f"Error closing client: {e}")
            finally:
                self.client = None
    
    def get_track_info(self, url):
        """Safely get track info."""
        if not self.client:
            raise RuntimeError("Client not initialized")
        
        return self.client.get_track_info(url)

# Usage
with SafeSpotifyClient() as client:
    track = client.get_track_info(url)
```

### 4. Error Context

```python
def add_error_context(func):
    """Decorator to add context to errors."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Add context to error
            context = {
                'function': func.__name__,
                'args': str(args)[:200],  # Truncate long args
                'kwargs': str(kwargs)[:200],
                'timestamp': datetime.now().isoformat()
            }
            
            # Create new exception with context
            enhanced_error = type(e)(f"{str(e)} | Context: {context}")
            enhanced_error.__cause__ = e
            raise enhanced_error
    
    return wrapper

@add_error_context
def get_track_with_context(client, url):
    return client.get_track_info(url)
```

---

## Next Steps

Now that you understand error handling:

1. 🔧 Set up [logging configuration](../getting-started/configuration.md#logging-configuration)
2. 🚀 Build [robust applications](../examples/advanced.md)
3. 📊 Implement [monitoring and alerting](../advanced/scaling.md)
4. 🛠️ Contribute to [error handling improvements](../contributing.md)

---

## Getting Help

If you encounter errors not covered here:

1. Check the [FAQ](../faq.md) for common issues
2. Review [troubleshooting guide](../troubleshooting.md)
3. Search [existing issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
4. Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
5. Report bugs on [Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues/new)