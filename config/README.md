# Configuration Directory

This directory contains configuration files for the SEO Mining application.

## Files

### `proxies.txt` (Optional)

**Format:** One proxy per line

**Example:**
```
http://user:pass@proxy1.example.com:8080
http://user:pass@proxy2.example.com:8080
socks5://user:pass@proxy3.example.com:1080
```

**Setup:**
1. Create `proxies.txt` in this directory
2. Add your proxy addresses (one per line)
3. Set `USE_PROXIES=true` in `backend/.env`
4. Set `DISABLE_DIRECT_CONNECTION=true` to force proxy usage

**Features:**
- Health monitoring with auto-disable on failures
- Multiple rotation strategies (round-robin, random, weighted)
- Per-proxy rate limiting
- Concurrent request support
- Geographic targeting capability

**When to use:**
- Large-scale scraping (100+ pages)
- Avoiding rate limits
- Maintaining anonymity
- Geographic targeting

**When NOT needed:**
- Small-scale testing (<10 pages)
- API-only workflows (ValueSerp doesn't need proxies)
- Local development

### `proxies.example.txt`

Template file showing proxy format. Copy to `proxies.txt` and add your proxies.

## Security

⚠️ **IMPORTANT:** Never commit `proxies.txt` to version control!

The `.gitignore` file already excludes `proxies.txt`, but double-check before committing.

## Environment Variables

Set these in `backend/.env`:

```bash
# Proxy Configuration
USE_PROXIES=true                    # Enable proxy usage
PROXY_FILE=config/proxies.txt       # Path to proxy file
PROXY_ROTATION=round-robin          # Strategy: round-robin, random, weighted
PROXY_TIMEOUT_SECONDS=10            # Request timeout per proxy
PROXY_RETRY_ATTEMPTS=3              # Retries before marking proxy dead
PROXY_HEALTH_CHECK_INTERVAL=300     # Health check every 5 minutes
DISABLE_DIRECT_CONNECTION=true      # Fail if no proxy available
```

## Proxy Requirements

### Format Support
- HTTP: `http://host:port` or `http://user:pass@host:port`
- HTTPS: `https://host:port` or `https://user:pass@host:port`
- SOCKS5: `socks5://host:port` or `socks5://user:pass@host:port`

### Recommended Specs
- **Count**: 50+ proxies for large-scale scraping
- **Type**: Residential or datacenter
- **Protocol**: HTTP/HTTPS (SOCKS5 if needed)
- **Authentication**: Username/password if required
- **Rotation**: Sticky sessions or rotating IPs
- **Geographic**: Match your target location (e.g., US for US SERPs)

### Testing Proxies

```powershell
# Test proxy connectivity
cd backend
docker-compose exec backend python -c "
import requests
proxy = 'http://user:pass@proxy.example.com:8080'
try:
    r = requests.get('https://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=10)
    print(f'✅ Proxy works: {r.json()}')
except Exception as e:
    print(f'❌ Proxy failed: {e}')
"
```

## Architecture

See `Plan/Proxy_Strategy.md` for detailed architecture:
- Proxy pool management
- Health monitoring
- Rotation strategies
- Failure handling
- Metrics tracking

## Troubleshooting

### Proxy Connection Failures

**Problem:** All proxies failing

**Solutions:**
1. Check proxy credentials are correct
2. Verify proxies are active (test manually)
3. Check proxy format in `proxies.txt`
4. Increase `PROXY_TIMEOUT_SECONDS`
5. Reduce `MAX_CONCURRENT_REQUESTS`

### Slow Scraping

**Problem:** Scraping is very slow

**Solutions:**
1. Increase concurrent requests: `MAX_CONCURRENT_REQUESTS=20`
2. Use faster proxies (residential vs datacenter)
3. Check proxy health: some may be dead
4. Enable sticky sessions for faster reuse

### Rate Limiting

**Problem:** Getting rate limited even with proxies

**Solutions:**
1. Increase `REQUEST_DELAY_SECONDS`
2. Use more proxies (increase pool size)
3. Enable `PROXY_ROTATION=random` for better distribution
4. Implement per-proxy rate limiting

### Geographic Targeting

**Problem:** Results from wrong location

**Solutions:**
1. Use proxies from target location
2. Set ValueSerp location parameter
3. Verify proxy IP location matches target

## Best Practices

### Development
- Start without proxies for simple testing
- Add proxies when scraping 10+ pages
- Use proxy pool for production workloads

### Production
- Maintain 50+ proxy pool for redundancy
- Enable health monitoring
- Set `DISABLE_DIRECT_CONNECTION=true`
- Monitor proxy success rates
- Rotate dead proxies regularly

### Security
- Never commit `proxies.txt`
- Use strong proxy authentication
- Rotate credentials periodically
- Monitor for unauthorized usage

### Performance
- Use concurrent requests (10-20)
- Enable caching to reduce requests
- Implement per-proxy rate limiting
- Monitor latency and adjust batch size

## Cost Analysis

### Without Proxies
- Direct scraping: Free but risky
- Risk: IP bans, rate limits, blocking
- Scale: Limited to ~10 requests/minute

### With 50 Proxies
- Proxy cost: $50-200/month (typical)
- Benefit: 10-50x throughput
- Scale: 500+ requests/minute
- Anonymity: High

### ROI Calculation
If you scrape 1,000 pages/month:
- Without proxies: High risk of bans, slow (hours)
- With proxies: Zero bans, fast (minutes)
- Time saved: ~10 hours/month
- Value: $50-200 cost vs $500+ time saved

## Support

For issues or questions:
1. Check `Plan/Proxy_Strategy.md` for architecture details
2. See `WINDOWS_GPU_SETUP.md` for troubleshooting
3. Review `QUICK_REFERENCE.md` for commands

---

**Next steps:**
1. Create `proxies.txt` with your proxies (or skip for now)
2. Configure `backend/.env` proxy settings
3. Test proxy connectivity
4. Start scraping!


