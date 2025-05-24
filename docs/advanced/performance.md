# Performance Optimization Guide

Learn how to maximize SpotifyScraper's performance for your use case.

## Table of Contents
- [Performance Basics](#performance-basics)
- [Client Optimization](#client-optimization)
- [Browser Selection](#browser-selection)
- [Caching Strategies](#caching-strategies)
- [Batch Processing](#batch-processing)
- [Concurrent Operations](#concurrent-operations)
- [Memory Management](#memory-management)
- [Network Optimization](#network-optimization)
- [Profiling & Benchmarking](#profiling--benchmarking)

---

## Performance Basics

### Understanding Performance Factors

1. **Network Latency**: Time to connect to Spotify
2. **Parsing Time**: Time to extract data from HTML/JSON
3. **Browser Overhead**: Selenium vs Requests
4. **Rate Limiting**: Spotify's request limits
5. **Memory Usage**: Data storage and processing

### Quick Wins

```python
# ✅ Good: Reuse client
client = SpotifyClient()
for url in urls:
    data = client.get_track_info(url)

# ❌ Bad: Create new client each time
for url in urls:
    client = SpotifyClient()  # Overhead!
    data = client.get_track_info(url)
```

---

## Client Optimization

### Client Reuse

Always reuse SpotifyClient instances:

```python
class MusicAnalyzer:
    def __init__(self):
        # Create once, use many times
        self.client = SpotifyClient()
    
    def analyze_tracks(self, urls):
        results = []
        for url in urls:
            data = self.client.get_track_info(url)
            results.append(self.process(data))
        return results
```

### Connection Pooling

SpotifyClient automatically uses connection pooling with requests:

```python
# Connection pooling is automatic with requests backend
client = SpotifyClient(browser_type="requests")

# Connections are reused for better performance
for i in range(100):
    client.get_track_info(urls[i])  # Reuses connections
```

---

## Browser Selection

### Performance Comparison

| Browser | Speed | Memory | Use Case |
|---------|-------|---------|----------|
| requests | Fast (100ms) | Low (50MB) | Most scenarios |
| selenium | Slow (2-5s) | High (500MB+) | Complex pages |

### When to Use Each

```python
# Use requests (default) for speed
client = SpotifyClient(browser_type="requests")

# Use selenium only when necessary
# (e.g., JavaScript-rendered content)
client = SpotifyClient(browser_type="selenium")
```

### Optimizing Selenium

If you must use Selenium:

```python
from spotify_scraper import SpotifyClient

# Selenium runs headless by default for better performance
client = SpotifyClient(browser_type="selenium")

# Always close when done to free memory
try:
    # Your operations
    pass
finally:
    client.close()
```

---

## Caching Strategies

### In-Memory Caching

```python
from functools import lru_cache
import hashlib

class CachedSpotifyClient:
    def __init__(self):
        self.client = SpotifyClient()
    
    @lru_cache(maxsize=1000)
    def get_track_cached(self, url):
        """Cache track data in memory."""
        return self.client.get_track_info(url)
    
    def get_track_info(self, url):
        # Normalize URL for better cache hits
        url = url.split('?')[0]  # Remove query params
        return self.get_track_cached(url)
```

### Disk Caching

```python
import json
import os
from datetime import datetime, timedelta
import hashlib

class DiskCachedClient:
    def __init__(self, cache_dir="cache", ttl_hours=24):
        self.client = SpotifyClient()
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, url):
        """Generate cache file path."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.json")
    
    def _is_cache_valid(self, cache_path):
        """Check if cache file is still valid."""
        if not os.path.exists(cache_path):
            return False
        
        mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - mtime < self.ttl
    
    def get_track_info(self, url):
        """Get track info with disk caching."""
        cache_path = self._get_cache_path(url)
        
        # Try cache first
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        
        # Fetch and cache
        data = self.client.get_track_info(url)
        with open(cache_path, 'w') as f:
            json.dump(data, f)
        
        return data
```

### Redis Caching

```python
import redis
import json

class RedisCachedClient:
    def __init__(self, redis_url="redis://localhost:6379", ttl=3600):
        self.client = SpotifyClient()
        self.redis = redis.from_url(redis_url)
        self.ttl = ttl
    
    def get_track_info(self, url):
        """Get track info with Redis caching."""
        # Try cache
        cached = self.redis.get(f"track:{url}")
        if cached:
            return json.loads(cached)
        
        # Fetch and cache
        data = self.client.get_track_info(url)
        self.redis.setex(
            f"track:{url}",
            self.ttl,
            json.dumps(data)
        )
        
        return data
```

---

## Batch Processing

### Efficient Batch Extraction

```python
import time
from typing import List, Dict, Any

def batch_extract(urls: List[str], delay: float = 0.5) -> List[Dict[str, Any]]:
    """Extract data from multiple URLs efficiently."""
    client = SpotifyClient()
    results = []
    
    total = len(urls)
    print(f"Processing {total} URLs...")
    
    for i, url in enumerate(urls):
        try:
            # Show progress
            if i % 10 == 0:
                print(f"Progress: {i}/{total} ({i/total*100:.1f}%)")
            
            # Extract data
            data = client.get_track_info(url)
            results.append({
                'url': url,
                'data': data,
                'success': True
            })
            
        except Exception as e:
            results.append({
                'url': url,
                'error': str(e),
                'success': False
            })
        
        # Rate limiting
        if i < total - 1:
            time.sleep(delay)
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\nCompleted: {successful}/{total} successful")
    
    return results
```

### Chunked Processing

```python
def process_in_chunks(urls: List[str], chunk_size: int = 50):
    """Process URLs in chunks to manage memory."""
    client = SpotifyClient()
    all_results = []
    
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i + chunk_size]
        print(f"\nProcessing chunk {i//chunk_size + 1}...")
        
        results = batch_extract(chunk)
        all_results.extend(results)
        
        # Optional: Save intermediate results
        save_checkpoint(all_results, f"checkpoint_{i}.json")
        
        # Rest between chunks
        if i + chunk_size < len(urls):
            print("Resting between chunks...")
            time.sleep(5)
    
    return all_results
```

---

## Concurrent Operations

### Thread Pool Executor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def concurrent_extract(urls: List[str], max_workers: int = 5):
    """Extract data concurrently with thread pool."""
    client = SpotifyClient()
    
    def extract_single(url):
        """Extract single URL with rate limiting."""
        try:
            data = client.get_track_info(url)
            return {'url': url, 'data': data, 'success': True}
        except Exception as e:
            return {'url': url, 'error': str(e), 'success': False}
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_url = {
            executor.submit(extract_single, url): url 
            for url in urls
        }
        
        # Process completed tasks
        for future in as_completed(future_to_url):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"✓ {result['url']}")
            else:
                print(f"✗ {result['url']}: {result['error']}")
    
    return results
```

### Async Processing (Advanced)

```python
import asyncio
import aiohttp
from typing import List, Dict

class AsyncSpotifyClient:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
    
    async def fetch_track(self, session, url):
        """Fetch single track asynchronously."""
        async with self.semaphore:
            # Convert to embed URL
            track_id = url.split('/')[-1].split('?')[0]
            embed_url = f"https://open.spotify.com/embed/track/{track_id}"
            
            try:
                async with session.get(embed_url) as response:
                    html = await response.text()
                    # Parse data (simplified)
                    return {'url': url, 'html_size': len(html), 'success': True}
            except Exception as e:
                return {'url': url, 'error': str(e), 'success': False}
    
    async def batch_fetch(self, urls: List[str]):
        """Fetch multiple tracks asynchronously."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_track(session, url) for url in urls]
            return await asyncio.gather(*tasks)

# Usage
async def main():
    client = AsyncSpotifyClient()
    urls = ["https://open.spotify.com/track/..." for _ in range(10)]
    results = await client.batch_fetch(urls)
    print(f"Fetched {len(results)} tracks")

# Run
asyncio.run(main())
```

---

## Memory Management

### Memory-Efficient Processing

```python
def process_large_dataset(urls: List[str], output_file: str):
    """Process large dataset without loading all in memory."""
    client = SpotifyClient()
    
    with open(output_file, 'w') as f:
        f.write('[\n')  # Start JSON array
        
        for i, url in enumerate(urls):
            try:
                data = client.get_track_info(url)
                
                # Write immediately, don't store
                if i > 0:
                    f.write(',\n')
                json.dump(data, f)
                
                # Clear any internal caches periodically
                if i % 100 == 0:
                    import gc
                    gc.collect()
                    
            except Exception as e:
                print(f"Error: {url} - {e}")
            
            time.sleep(0.5)  # Rate limit
        
        f.write('\n]')  # End JSON array
```

### Generator Pattern

```python
def track_generator(urls: List[str]):
    """Generate track data one at a time."""
    client = SpotifyClient()
    
    for url in urls:
        try:
            yield client.get_track_info(url)
            time.sleep(0.5)  # Rate limit
        except Exception as e:
            print(f"Error: {url} - {e}")
            yield None

# Memory efficient usage
for track_data in track_generator(urls):
    if track_data:
        # Process immediately, don't store
        process_track(track_data)
```

---

## Network Optimization

### Retry Logic

```python
import time
from typing import Optional

def extract_with_retry(url: str, max_retries: int = 3) -> Optional[Dict]:
    """Extract with exponential backoff retry."""
    client = SpotifyClient()
    
    for attempt in range(max_retries):
        try:
            return client.get_track_info(url)
        
        except NetworkError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1} after {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        
        except Exception as e:
            print(f"Unrecoverable error: {e}")
            return None
```

### Request Optimization

```python
# Use appropriate timeouts
client = SpotifyClient()

# For requests backend, timeouts are built-in
# For selenium, ensure proper cleanup
```

---

## Profiling & Benchmarking

### Simple Benchmarking

```python
import time
from statistics import mean, stdev

def benchmark_extraction(urls: List[str], iterations: int = 3):
    """Benchmark extraction performance."""
    client = SpotifyClient()
    
    times = []
    for i in range(iterations):
        start = time.time()
        
        for url in urls:
            try:
                client.get_track_info(url)
            except:
                pass
        
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Iteration {i+1}: {elapsed:.2f}s")
    
    print(f"\nResults:")
    print(f"Average: {mean(times):.2f}s")
    print(f"Std Dev: {stdev(times):.2f}s")
    print(f"Per URL: {mean(times)/len(urls):.3f}s")
```

### Memory Profiling

```python
import tracemalloc

def profile_memory_usage():
    """Profile memory usage."""
    tracemalloc.start()
    
    # Your operations
    client = SpotifyClient()
    data = []
    for i in range(100):
        data.append(client.get_track_info(f"...track_{i}"))
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
    
    tracemalloc.stop()
```

---

## Performance Best Practices

### Do's ✅

1. **Reuse client instances**
2. **Use requests backend when possible**
3. **Implement caching for repeated requests**
4. **Add appropriate delays between requests**
5. **Process data in chunks for large datasets**
6. **Close Selenium browsers when done**
7. **Handle errors gracefully**

### Don'ts ❌

1. **Don't create new clients repeatedly**
2. **Don't use Selenium unless necessary**
3. **Don't make parallel requests without limits**
4. **Don't ignore rate limits**
5. **Don't load entire datasets into memory**
6. **Don't forget to close resources**

---

## Performance Checklist

Before deploying to production:

- [ ] Client instances are reused
- [ ] Appropriate browser backend selected
- [ ] Caching implemented (if applicable)
- [ ] Rate limiting in place
- [ ] Error handling and retries
- [ ] Memory usage monitored
- [ ] Resources properly closed
- [ ] Benchmarked performance
- [ ] Logging configured appropriately

---

## Real-World Example

Here's a complete, optimized data extraction system:

```python
import time
import json
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

class OptimizedSpotifyExtractor:
    def __init__(self, cache_size=1000, max_workers=3):
        self.client = SpotifyClient()
        self.max_workers = max_workers
        self.stats = {
            'requests': 0,
            'cache_hits': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
    
    @lru_cache(maxsize=1000)
    def _extract_cached(self, url: str) -> Dict[str, Any]:
        """Extract with caching."""
        self.stats['requests'] += 1
        return self.client.get_track_info(url)
    
    def extract_track(self, url: str) -> Dict[str, Any]:
        """Extract single track with caching."""
        # Normalize URL
        url = url.split('?')[0]
        
        # Check if cached
        if url in self._extract_cached.cache_info()._cache:
            self.stats['cache_hits'] += 1
        
        try:
            return self._extract_cached(url)
        except Exception as e:
            self.stats['errors'] += 1
            raise
    
    def extract_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Extract batch with rate limiting."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for i, url in enumerate(urls):
                # Submit with delay
                if i > 0:
                    time.sleep(0.5)  # Rate limit
                
                future = executor.submit(self.extract_track, url)
                futures.append((url, future))
            
            # Collect results
            for url, future in futures:
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    print(f"Failed: {url} - {e}")
                    results.append(None)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'total_requests': self.stats['requests'],
            'cache_hits': self.stats['cache_hits'],
            'cache_hit_rate': self.stats['cache_hits'] / max(1, self.stats['requests']),
            'errors': self.stats['errors'],
            'elapsed_seconds': elapsed,
            'requests_per_second': self.stats['requests'] / max(1, elapsed)
        }

# Usage
extractor = OptimizedSpotifyExtractor()

# Extract batch
urls = ["https://open.spotify.com/track/..." for _ in range(100)]
results = extractor.extract_batch(urls)

# Show stats
stats = extractor.get_stats()
print(f"Performance: {stats['requests_per_second']:.2f} req/s")
print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
```

This optimized system includes:
- Client reuse
- In-memory caching
- Concurrent processing with limits
- Rate limiting
- Performance statistics
- Error handling

Expected performance: 1-2 requests/second with 0.5s delay, higher with caching.