# Scaling SpotifyScraper

This guide covers strategies and best practices for scaling SpotifyScraper to handle large-scale data extraction operations.

## Overview

When working with thousands or millions of tracks, albums, and playlists, you need to consider:

- **Rate limiting** - Avoiding Spotify's anti-scraping measures
- **Resource management** - CPU, memory, and network optimization
- **Data pipeline** - Efficient data processing and storage
- **Fault tolerance** - Handling failures gracefully
- **Monitoring** - Tracking progress and performance

## Architecture for Scale

### 1. Distributed Architecture

```python
# producer.py - Generates work items
import redis
import json
from spotify_scraper import SpotifyClient

class WorkProducer:
    def __init__(self, redis_host='localhost'):
        self.redis = redis.Redis(host=redis_host, decode_responses=True)
        self.client = SpotifyClient()
    
    def produce_artist_work(self, artist_id):
        """Generate work items for an artist's discography"""
        artist = self.client.get_artist(artist_id)
        
        # Queue albums
        for album in artist.get('albums', []):
            work_item = {
                'type': 'album',
                'id': album['id'],
                'priority': 1
            }
            self.redis.lpush('work_queue', json.dumps(work_item))
        
        # Queue top tracks
        work_item = {
            'type': 'artist_tracks',
            'id': artist_id,
            'priority': 2
        }
        self.redis.lpush('work_queue', json.dumps(work_item))
``````python
# worker.py - Processes work items
import redis
import json
import time
import logging
from spotify_scraper import SpotifyClient
from spotify_scraper.config import Config

class Worker:
    def __init__(self, worker_id, redis_host='localhost'):
        self.worker_id = worker_id
        self.redis = redis.Redis(host=redis_host, decode_responses=True)
        self.client = SpotifyClient(
            config=Config(
                cache_enabled=True,
                request_timeout=30,
                max_retries=5
            )
        )
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format=f'[Worker-{self.worker_id}] %(asctime)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def process_work_item(self, work_item):
        """Process a single work item"""
        item_type = work_item['type']
        item_id = work_item['id']
        
        try:
            if item_type == 'album':
                data = self.client.get_album(item_id)
                self.store_result('album', item_id, data)
                
                # Generate track work items
                for track in data.get('tracks', []):
                    track_work = {
                        'type': 'track',
                        'id': track['id'],
                        'priority': 3
                    }
                    self.redis.lpush('work_queue', json.dumps(track_work))
            
            elif item_type == 'track':
                data = self.client.get_track(item_id)
                self.store_result('track', item_id, data)            elif item_type == 'artist_tracks':
                # Implement artist top tracks extraction
                pass
            
            self.logger.info(f"Processed {item_type} {item_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to process {item_type} {item_id}: {e}")
            self.handle_failure(work_item, str(e))
    
    def store_result(self, result_type, item_id, data):
        """Store extracted data"""
        key = f"result:{result_type}:{item_id}"
        self.redis.setex(key, 86400, json.dumps(data))  # 24 hour TTL
    
    def handle_failure(self, work_item, error):
        """Handle failed work items"""
        work_item['retry_count'] = work_item.get('retry_count', 0) + 1
        work_item['last_error'] = error
        
        if work_item['retry_count'] < 3:
            # Requeue with backoff
            delay = 60 * work_item['retry_count']
            self.redis.zadd('delayed_queue', 
                           {json.dumps(work_item): time.time() + delay})
        else:
            # Move to dead letter queue
            self.redis.lpush('failed_queue', json.dumps(work_item))
    
    def run(self):
        """Main worker loop"""
        self.logger.info("Worker started")
        
        while True:
            # Check for delayed items
            self.process_delayed_items()
            
            # Get work item
            work_json = self.redis.brpop('work_queue', timeout=5)
            if work_json:
                work_item = json.loads(work_json[1])
                self.process_work_item(work_item)
                
                # Rate limiting
                time.sleep(0.5)  # Adjust based on your needs