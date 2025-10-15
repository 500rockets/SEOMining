# ValueSerp API Documentation

## Overview
ValueSerp provides programmatic access to Google search results. We use it to fetch the top 10 organic search results for target keywords.

## API Endpoint

**Base URL**: `https://api.valueserp.com/search`

**Your Configuration**:
```
API Key: 12589F7B3D6B4BD48F6737487FEE83DA
Location: 98146, Washington, United States
GL (country): us
HL (language): en
Google Domain: google.com
```

## Example Request

```bash
curl "https://api.valueserp.com/search?api_key=12589F7B3D6B4BD48F6737487FEE83DA&q=keyword+here&location=98146%2C+Washington%2C+United+States&gl=us&hl=en&google_domain=google.com"
```

## Response Structure

### Key Fields We'll Use:

#### 1. Request Info
```json
"request_info": {
  "success": true,
  "topup_credits_remaining": 9986,
  "credits_used_this_request": 1
}
```
- Monitor credit usage
- Check success status

#### 2. Organic Results (Top 10)
```json
"organic_results": [
  {
    "position": 1,
    "title": "Page Title",
    "link": "https://example.com/page",
    "domain": "example.com",
    "snippet": "Page description...",
    "prerender": false
  }
]
```

**Fields to Extract**:
- `position`: Ranking position (1-10)
- `title`: Page title
- `link`: URL to spider/scrape
- `domain`: Domain name
- `snippet`: Meta description
- `displayed_link`: Displayed URL

#### 3. Related Searches
```json
"related_searches": [
  {
    "query": "related keyword",
    "link": "https://www.google.com/search?q=..."
  }
]
```
- Use for keyword expansion (future feature)

## Implementation Plan

### Module: `fetch/valueserp_client.py`

```python
class ValueSerpClient:
    def __init__(self, api_key: str):
        """Initialize with API key from .env"""
        
    def search(self, keyword: str, num_results: int = 10) -> dict:
        """
        Fetch search results for a keyword
        Returns parsed response with organic results
        """
        
    def get_organic_results(self, response: dict) -> list:
        """
        Extract and normalize organic results
        Returns list of competitor URLs with metadata
        """
        
    def check_credits(self) -> int:
        """Check remaining API credits"""
```

### Data Storage

For each search, we'll save:

```
data/raw/{keyword-slug}/
├── metadata.json          # Full API response
├── organic_results.json   # Cleaned list of competitors
└── search_params.json     # Search parameters used
```

**metadata.json** example:
```json
{
  "keyword": "keyword here",
  "search_date": "2025-10-15T14:23:44.975Z",
  "location": "98146, Washington, United States",
  "credits_used": 1,
  "credits_remaining": 9986,
  "organic_results": [
    {
      "position": 1,
      "title": "Keywords Everywhere",
      "link": "https://keywordseverywhere.com/",
      "domain": "keywordseverywhere.com",
      "snippet": "This tool helps with SEO...",
      "fetched": false,
      "fetch_date": null,
      "file_path": null
    }
  ]
}
```

## Rate Limiting & Best Practices

1. **Credit Monitoring**: Track remaining credits before each call
2. **Caching**: Store results to avoid duplicate API calls
3. **Error Handling**: 
   - Handle API timeouts
   - Check `success` flag in response
   - Log failed requests
4. **Cost Optimization**:
   - Cache results for X days (configurable)
   - Only re-fetch if keyword/location changes
   - Batch multiple keywords if needed

## Error Scenarios

### Insufficient Credits
```json
{
  "request_info": {
    "success": false,
    "error": "Insufficient credits"
  }
}
```
**Action**: Alert user, suggest credit top-up

### Invalid API Key
```json
{
  "request_info": {
    "success": false,
    "error": "Invalid API key"
  }
}
```
**Action**: Check .env configuration

### Rate Limit
```json
{
  "request_info": {
    "success": false,
    "error": "Rate limit exceeded"
  }
}
```
**Action**: Implement exponential backoff, retry after delay

## Integration with Next Steps

```
ValueSerp API
    ↓
Organic Results (10 URLs)
    ↓
For each URL:
    ↓
fetch/page_scraper.py
    ↓
Save HTML → data/raw/{keyword}/competitor_{n}.html
    ↓
analyze/text_extractor.py
    ↓
Clean Text → data/raw/{keyword}/competitor_{n}_text.txt
    ↓
analyze/embedder.py
    ↓
Embeddings → data/processed/{keyword}/embeddings.pkl
```

## Testing Strategy

1. **Unit Tests**: Mock API responses
2. **Integration Tests**: Use test API key with known keyword
3. **Validation**: Verify we get exactly 10 organic results
4. **Edge Cases**:
   - Keywords with no results
   - Keywords with <10 results
   - Special characters in keywords
   - Different locations/languages

## Security Notes

⚠️ **IMPORTANT**: Never commit the actual API key!
- Store in `.env` file (gitignored)
- Use `config.example.env` as template
- Rotate keys if accidentally exposed
- Monitor usage dashboard for anomalies

## Links

- [ValueSerp Documentation](https://www.valueserp.com/docs)
- [API Dashboard](https://www.valueserp.com/dashboard) (for credit monitoring)

