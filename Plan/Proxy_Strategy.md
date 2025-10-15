# Proxy Strategy & Implementation

## Overview
To avoid rate limiting, IP bans, and ensure reliable scraping, **all web requests go through a pool of 50 rotating proxies**. Direct connections are disabled by default.

## Proxy Pool Configuration

### Setup
**File**: `config/proxies.txt`

**Format** (one proxy per line):
```
http://proxy1.example.com:8080
http://user:pass@proxy2.example.com:3128
socks5://proxy3.example.com:1080
```

### Supported Proxy Types
- HTTP/HTTPS proxies
- SOCKS4/SOCKS5 proxies
- Authenticated proxies (username:password)
- Unauthenticated proxies

## Rotation Strategies

### 1. Round-Robin (Default)
- Cycle through proxies sequentially
- Fair distribution of load
- Predictable behavior

```python
class RoundRobinProxyPool:
    def __init__(self, proxies: list):
        self.proxies = proxies
        self.current_index = 0
    
    def get_next_proxy(self) -> str:
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
```

### 2. Random Selection
- Pick random proxy for each request
- Better for avoiding patterns
- More unpredictable

```python
import random

class RandomProxyPool:
    def get_next_proxy(self) -> str:
        return random.choice(self.proxies)
```

### 3. Weighted Selection (Advanced)
- Prioritize faster/more reliable proxies
- Track success rates
- Automatically favor better performers

```python
class WeightedProxyPool:
    def __init__(self, proxies: list):
        self.proxy_stats = {
            proxy: {'success': 0, 'failure': 0, 'avg_response_time': 0}
            for proxy in proxies
        }
    
    def get_next_proxy(self) -> str:
        # Select based on success rate and response time
        weights = self.calculate_weights()
        return random.choices(self.proxies, weights=weights)[0]
```

### 4. Sticky Sessions (Domain-Based)
- Use same proxy for all requests to a specific domain
- Useful for sites that track session/IP consistency
- Falls back to new proxy on failure

```python
class StickySessionProxyPool:
    def __init__(self, proxies: list):
        self.domain_proxy_map = {}
        self.proxies = proxies
    
    def get_proxy_for_domain(self, domain: str) -> str:
        if domain not in self.domain_proxy_map:
            self.domain_proxy_map[domain] = random.choice(self.proxies)
        return self.domain_proxy_map[domain]
```

## Health Monitoring

### Proxy Validation
**Run on startup and periodically:**

```python
async def validate_proxy(proxy: str) -> bool:
    """
    Test proxy by making request to test endpoint
    Returns True if proxy works, False otherwise
    """
    try:
        response = requests.get(
            'https://httpbin.org/ip',
            proxies={'http': proxy, 'https': proxy},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"Proxy {proxy} failed validation: {e}")
        return False
```

### Metrics to Track
```python
class ProxyMetrics:
    proxy: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    last_success: datetime
    last_failure: datetime
    consecutive_failures: int
    is_healthy: bool
```

### Auto-Disable Failing Proxies
- **Threshold**: Disable after 3 consecutive failures
- **Cooldown**: Re-enable after 5 minutes
- **Health Check**: Periodic validation every 5 minutes

```python
class ProxyHealthManager:
    FAILURE_THRESHOLD = 3
    COOLDOWN_SECONDS = 300
    
    def mark_failure(self, proxy: str):
        metrics = self.get_metrics(proxy)
        metrics.consecutive_failures += 1
        
        if metrics.consecutive_failures >= self.FAILURE_THRESHOLD:
            self.disable_proxy(proxy)
            self.schedule_reenable(proxy, self.COOLDOWN_SECONDS)
    
    def mark_success(self, proxy: str):
        metrics = self.get_metrics(proxy)
        metrics.consecutive_failures = 0
        metrics.is_healthy = True
```

## Request Implementation

### Module: `utils/proxy_manager.py`

```python
import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manages proxy pool and rotation"""
    
    def __init__(self, proxy_file: str, rotation_strategy: str = 'round-robin'):
        self.proxies = self.load_proxies(proxy_file)
        self.strategy = self.init_strategy(rotation_strategy)
        self.health_manager = ProxyHealthManager(self.proxies)
        self.direct_connection_disabled = True
        
    def load_proxies(self, file_path: str) -> list:
        """Load proxies from config file"""
        with open(file_path, 'r') as f:
            proxies = [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith('#')
            ]
        logger.info(f"Loaded {len(proxies)} proxies")
        return proxies
    
    def get_proxy(self, domain: Optional[str] = None) -> Dict[str, str]:
        """Get next proxy based on strategy"""
        proxy_url = self.strategy.get_next_proxy(domain)
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def make_request(self, url: str, **kwargs) -> requests.Response:
        """Make request through proxy pool with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            proxy_dict = self.get_proxy()
            proxy_url = proxy_dict['http']
            
            try:
                response = requests.get(
                    url,
                    proxies=proxy_dict,
                    timeout=10,
                    **kwargs
                )
                
                # Mark success
                self.health_manager.mark_success(proxy_url)
                return response
                
            except Exception as e:
                logger.warning(
                    f"Request failed with proxy {proxy_url}: {e}"
                )
                self.health_manager.mark_failure(proxy_url)
                
                if attempt == max_retries - 1:
                    raise
                
        raise Exception("All proxy attempts failed")
```

### Integration with Scraper

```python
# fetch/page_scraper.py

from utils.proxy_manager import ProxyManager

class PageScraper:
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
    
    def fetch_page(self, url: str) -> str:
        """Fetch page HTML through proxy"""
        response = self.proxy_manager.make_request(
            url,
            headers={'User-Agent': 'SEOMiningBot/1.0'},
            timeout=10
        )
        return response.text
    
    async def fetch_pages_concurrent(self, urls: list) -> dict:
        """Fetch multiple pages concurrently using different proxies"""
        # Each URL gets a different proxy from the pool
        # Up to 10 concurrent requests (configurable)
        pass
```

## Configuration Options

### Environment Variables
```bash
# Enable proxy usage
USE_PROXIES=true

# Proxy list file
PROXY_FILE=config/proxies.txt

# Rotation strategy: round-robin, random, weighted, sticky
PROXY_ROTATION=round-robin

# Timeout for proxy requests (seconds)
PROXY_TIMEOUT_SECONDS=10

# Retry attempts per proxy
PROXY_RETRY_ATTEMPTS=3

# Health check interval (seconds)
PROXY_HEALTH_CHECK_INTERVAL=300

# Disable direct connections (fail if all proxies down)
DISABLE_DIRECT_CONNECTION=true
```

## Benefits of Proxy Pool

### 1. **Avoid Rate Limits**
- Distribute requests across 50 IPs
- Each IP handles fewer requests
- Reduces chance of being flagged

### 2. **Bypass Geographic Restrictions**
- Use proxies from target location
- Get accurate localized results
- Match search location if needed

### 3. **Resilience**
- If one proxy fails, use another
- No single point of failure
- Automatic failover

### 4. **Parallel Processing**
- Fetch 10 pages concurrently
- Each through different proxy
- Significantly faster than sequential

### 5. **Anonymity**
- Harder to track/block scraping activity
- Appears as normal traffic from multiple users
- Reduces risk of IP bans

## Performance Optimization

### With 50 Proxies:
- **Concurrent Requests**: 10-20 simultaneous
- **Per-Proxy Rate**: 1 request every 5 seconds
- **Total Throughput**: ~10 requests/second
- **Fetch 10 Pages**: ~1-2 seconds (vs 10+ seconds direct)

### Recommended Settings:
```python
MAX_CONCURRENT_REQUESTS = 10
REQUEST_DELAY_PER_PROXY = 0.5  # seconds
PROXY_POOL_SIZE = 50
ROTATION = 'round-robin'
```

## Testing & Validation

### 1. Validate All Proxies on Startup
```bash
python scripts/validate_proxies.py
```

### 2. Monitor Proxy Health Dashboard
```bash
python scripts/proxy_dashboard.py
```

### 3. Test Single URL Through Proxy Pool
```python
from utils.proxy_manager import ProxyManager

pm = ProxyManager('config/proxies.txt')
response = pm.make_request('https://example.com')
print(f"Fetched via proxy: {response.status_code}")
```

## Security Considerations

1. **Proxy Credentials**: Store encrypted or in secure .env
2. **Proxy Provider Trust**: Use reputable proxy services
3. **Data Leakage**: Ensure proxies don't log/cache content
4. **Authentication**: Use authenticated proxies when possible
5. **Rotation**: Regular proxy IP rotation to avoid patterns

## Troubleshooting

### Issue: All Proxies Failing
**Solutions**:
- Check proxy credentials
- Validate proxy format
- Test proxy connectivity manually
- Check proxy service status
- Ensure firewall allows proxy connections

### Issue: Slow Response Times
**Solutions**:
- Use 'weighted' rotation to favor faster proxies
- Increase timeout settings
- Reduce concurrent request limit
- Check proxy geographic location

### Issue: Some Sites Block Proxies
**Solutions**:
- Use residential proxies (not datacenter)
- Implement better user-agent rotation
- Add cookie handling
- Use sticky sessions for that domain
- Consider premium proxy services

## Future Enhancements

1. **Smart Proxy Selection**: ML-based proxy selection by domain
2. **Geographic Optimization**: Match proxy location to target site
3. **Cost Tracking**: Monitor proxy service usage/costs
4. **Proxy Marketplace Integration**: Auto-purchase more proxies if needed
5. **Fingerprint Rotation**: Rotate browser fingerprints with proxies

