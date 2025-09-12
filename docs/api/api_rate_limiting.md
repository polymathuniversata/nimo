# Nimo Platform - API Rate Limiting Guide

## Overview

This document outlines the rate limiting policies, implementation details, and best practices for the Nimo Platform API. Rate limiting helps ensure fair usage, prevents abuse, and maintains optimal performance for all users.

## Rate Limiting Policies

### Default Rate Limits

| Endpoint Category | Rate Limit | Window | Burst Allowance |
|------------------|------------|---------|-----------------|
| **Authentication** | 5 requests | per minute | 2 requests |
| **User Management** | 30 requests | per minute | 10 requests |
| **Contributions** | 60 requests | per minute | 20 requests |
| **MeTTa Operations** | 10 requests | per minute | 3 requests |
| **Blockchain Operations** | 15 requests | per minute | 5 requests |
| **Public Endpoints** | 100 requests | per minute | 30 requests |
| **WebSocket Connections** | 5 connections | per user | N/A |

### Premium Rate Limits (For Verified Organizations)

| Endpoint Category | Rate Limit | Window | Burst Allowance |
|------------------|------------|---------|-----------------|
| **Authentication** | 20 requests | per minute | 5 requests |
| **User Management** | 100 requests | per minute | 30 requests |
| **Contributions** | 200 requests | per minute | 60 requests |
| **MeTTa Operations** | 50 requests | per minute | 15 requests |
| **Blockchain Operations** | 60 requests | per minute | 20 requests |
| **Public Endpoints** | 500 requests | per minute | 150 requests |
| **WebSocket Connections** | 20 connections | per user | N/A |

## Implementation Details

### Backend Implementation

The rate limiting is implemented using Flask-Limiter with Redis as the storage backend:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=1)

# Initialize Flask-Limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/1",
    default_limits=["1000 per hour", "100 per minute"]
)
```

### Rate Limiting Strategies

#### 1. IP-Based Rate Limiting
```python
@app.route('/api/public/stats')
@limiter.limit("100 per minute")
def public_stats():
    # Public endpoint with IP-based limiting
    pass
```

#### 2. User-Based Rate Limiting
```python
@app.route('/api/user/profile')
@limiter.limit("30 per minute", key_func=get_user_id)
def user_profile():
    # User-specific rate limiting
    pass

def get_user_id():
    # Extract user ID from JWT token
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token:
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload['user_id']
        except:
            pass
    return get_remote_address()
```

#### 3. Endpoint-Specific Rate Limiting
```python
@app.route('/api/metta/verify')
@limiter.limit("10 per minute", key_func=get_user_id)
def metta_verification():
    # Intensive MeTTa operations with strict limits
    pass

@app.route('/api/blockchain/verify')
@limiter.limit("15 per minute", key_func=get_user_id)
def blockchain_verification():
    # Blockchain operations with moderate limits
    pass
```

## Endpoint-Specific Rate Limits

### Authentication Endpoints

```
POST /api/auth/login          - 5/min per IP
POST /api/auth/register       - 5/min per IP
POST /api/auth/refresh        - 10/min per user
POST /api/auth/logout         - 20/min per user
POST /api/auth/reset-password - 3/min per IP
```

### User Management Endpoints

```
GET  /api/user/profile        - 30/min per user
PUT  /api/user/profile        - 10/min per user
GET  /api/user/contributions  - 60/min per user
POST /api/user/avatar         - 5/min per user
DELETE /api/user/account      - 1/hour per user
```

### Contribution Endpoints

```
GET  /api/contributions       - 60/min per user
POST /api/contributions       - 20/min per user
PUT  /api/contributions/:id   - 30/min per user
DELETE /api/contributions/:id - 10/min per user
POST /api/contributions/verify - 10/min per user
```

### MeTTa AI Endpoints

```
POST /api/metta/verify        - 10/min per user
POST /api/metta/analyze       - 15/min per user
GET  /api/metta/rules         - 30/min per user
POST /api/metta/rules         - 5/min per user
```

### Blockchain Endpoints

```
POST /api/blockchain/verify   - 15/min per user
GET  /api/blockchain/balance  - 30/min per user
POST /api/blockchain/transfer - 10/min per user
GET  /api/blockchain/history  - 60/min per user
```

### Public Endpoints

```
GET  /api/public/stats        - 100/min per IP
GET  /api/public/leaderboard  - 100/min per IP
GET  /api/health              - No limit
GET  /api/version             - No limit
```

## Rate Limit Headers

The API returns rate limiting information in response headers:

```
X-RateLimit-Limit: 60          // Rate limit per window
X-RateLimit-Remaining: 45       // Remaining requests in current window  
X-RateLimit-Reset: 1692123456   // Unix timestamp when window resets
X-RateLimit-Window: 60          // Window duration in seconds
Retry-After: 15                 // Seconds to wait before next request (when rate limited)
```

### Example Response Headers

**Successful Request:**
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1692123456
X-RateLimit-Window: 60
Content-Type: application/json

{
  "status": "success",
  "data": {...}
}
```

**Rate Limited Request:**
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1692123456
X-RateLimit-Window: 60
Retry-After: 30
Content-Type: application/json

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 30 seconds.",
    "details": {
      "limit": 60,
      "window": 60,
      "reset_time": 1692123456
    }
  }
}
```

## Rate Limiting Tiers

### Tier 1: Basic (Default)
- **Cost**: Free
- **Monthly Quota**: 100,000 requests
- **Rate Limits**: Standard limits as listed above
- **Burst**: Limited burst capacity

### Tier 2: Premium
- **Cost**: $49/month
- **Monthly Quota**: 1,000,000 requests  
- **Rate Limits**: 3x standard limits
- **Burst**: Enhanced burst capacity
- **Priority Support**: Yes

### Tier 3: Enterprise
- **Cost**: Custom pricing
- **Monthly Quota**: Custom/Unlimited
- **Rate Limits**: Custom limits
- **Burst**: Custom burst capacity
- **Dedicated Support**: Yes
- **SLA**: 99.9% uptime

## Client-Side Implementation

### JavaScript/React Example

```javascript
class NimoAPI {
  constructor(baseURL, apiKey) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
    this.rateLimitInfo = {};
  }

  async makeRequest(endpoint, options = {}) {
    // Check if we're rate limited
    if (this.isRateLimited(endpoint)) {
      const waitTime = this.getWaitTime(endpoint);
      throw new Error(`Rate limited. Wait ${waitTime} seconds.`);
    }

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      // Update rate limit info from headers
      this.updateRateLimitInfo(endpoint, response.headers);

      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After');
        throw new RateLimitError(`Rate limited. Retry after ${retryAfter} seconds.`);
      }

      return response;
    } catch (error) {
      if (error instanceof RateLimitError) {
        // Implement exponential backoff
        await this.backoff(endpoint);
        return this.makeRequest(endpoint, options);
      }
      throw error;
    }
  }

  updateRateLimitInfo(endpoint, headers) {
    const category = this.getEndpointCategory(endpoint);
    this.rateLimitInfo[category] = {
      limit: parseInt(headers.get('X-RateLimit-Limit')),
      remaining: parseInt(headers.get('X-RateLimit-Remaining')),
      reset: parseInt(headers.get('X-RateLimit-Reset')),
      window: parseInt(headers.get('X-RateLimit-Window'))
    };
  }

  isRateLimited(endpoint) {
    const category = this.getEndpointCategory(endpoint);
    const info = this.rateLimitInfo[category];
    
    if (!info) return false;
    
    const now = Date.now() / 1000;
    return info.remaining === 0 && now < info.reset;
  }

  getWaitTime(endpoint) {
    const category = this.getEndpointCategory(endpoint);
    const info = this.rateLimitInfo[category];
    const now = Date.now() / 1000;
    return Math.max(0, info.reset - now);
  }

  async backoff(endpoint) {
    const waitTime = this.getWaitTime(endpoint) * 1000;
    const jitter = Math.random() * 1000; // Add jitter
    await new Promise(resolve => setTimeout(resolve, waitTime + jitter));
  }

  getEndpointCategory(endpoint) {
    if (endpoint.startsWith('/auth')) return 'auth';
    if (endpoint.startsWith('/user')) return 'user';
    if (endpoint.startsWith('/contributions')) return 'contributions';
    if (endpoint.startsWith('/metta')) return 'metta';
    if (endpoint.startsWith('/blockchain')) return 'blockchain';
    return 'public';
  }
}

class RateLimitError extends Error {
  constructor(message) {
    super(message);
    this.name = 'RateLimitError';
  }
}
```

### Python Client Example

```python
import time
import requests
from typing import Dict, Optional

class NimoAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.rate_limit_info: Dict = {}
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def make_request(self, endpoint: str, method: str = 'GET', **kwargs):
        if self._is_rate_limited(endpoint):
            wait_time = self._get_wait_time(endpoint)
            raise RateLimitException(f"Rate limited. Wait {wait_time} seconds.")

        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            self._update_rate_limit_info(endpoint, response.headers)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                return self.make_request(endpoint, method, **kwargs)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # Implement exponential backoff for server errors
            if hasattr(e, 'response') and e.response.status_code >= 500:
                self._backoff(endpoint)
                return self.make_request(endpoint, method, **kwargs)
            raise

    def _is_rate_limited(self, endpoint: str) -> bool:
        category = self._get_endpoint_category(endpoint)
        info = self.rate_limit_info.get(category)
        
        if not info:
            return False
            
        return info['remaining'] == 0 and time.time() < info['reset']

    def _get_wait_time(self, endpoint: str) -> float:
        category = self._get_endpoint_category(endpoint)
        info = self.rate_limit_info.get(category, {})
        return max(0, info.get('reset', 0) - time.time())

    def _update_rate_limit_info(self, endpoint: str, headers):
        category = self._get_endpoint_category(endpoint)
        self.rate_limit_info[category] = {
            'limit': int(headers.get('X-RateLimit-Limit', 0)),
            'remaining': int(headers.get('X-RateLimit-Remaining', 0)),
            'reset': int(headers.get('X-RateLimit-Reset', 0)),
            'window': int(headers.get('X-RateLimit-Window', 60))
        }

    def _get_endpoint_category(self, endpoint: str) -> str:
        if endpoint.startswith('/auth'):
            return 'auth'
        elif endpoint.startswith('/user'):
            return 'user'
        elif endpoint.startswith('/contributions'):
            return 'contributions'
        elif endpoint.startswith('/metta'):
            return 'metta'
        elif endpoint.startswith('/blockchain'):
            return 'blockchain'
        else:
            return 'public'

    def _backoff(self, endpoint: str):
        # Exponential backoff with jitter
        wait_time = min(60, 2 ** self._get_retry_count(endpoint))
        jitter = wait_time * 0.1 * (0.5 - random.random())
        time.sleep(wait_time + jitter)

class RateLimitException(Exception):
    pass
```

## Monitoring and Analytics

### Metrics to Track

1. **Request Volume**
   - Requests per minute/hour/day
   - Peak traffic periods
   - Growth trends

2. **Rate Limiting Events**
   - Number of rate-limited requests
   - Most frequently limited endpoints
   - User behavior patterns

3. **Performance Impact**
   - Response time correlation with rate limiting
   - Error rates by endpoint category
   - User satisfaction metrics

### Monitoring Dashboard

Key metrics to display:

```json
{
  "current_metrics": {
    "total_requests_per_minute": 1250,
    "rate_limited_requests_per_minute": 15,
    "unique_users_active": 342,
    "most_used_endpoints": [
      "/api/contributions",
      "/api/user/profile", 
      "/api/public/stats"
    ]
  },
  "rate_limit_violations": {
    "last_hour": 89,
    "by_endpoint": {
      "/api/metta/verify": 34,
      "/api/blockchain/verify": 28,
      "/api/auth/login": 27
    },
    "by_user_type": {
      "free_tier": 76,
      "premium_tier": 13
    }
  }
}
```

## Best Practices

### For API Users

1. **Respect Rate Limits**
   - Check rate limit headers
   - Implement client-side rate limiting
   - Use appropriate retry strategies

2. **Optimize Request Patterns**
   - Batch operations when possible
   - Cache responses appropriately
   - Use webhooks instead of polling

3. **Handle Rate Limit Errors Gracefully**
   - Implement exponential backoff
   - Show meaningful error messages to users
   - Queue requests when rate limited

4. **Monitor Your Usage**
   - Track your request patterns
   - Set up alerts for approaching limits
   - Upgrade tier when necessary

### For API Providers

1. **Set Reasonable Limits**
   - Balance protection with usability
   - Consider different use cases
   - Provide clear documentation

2. **Implement Graceful Degradation**
   - Priority queues for different user tiers
   - Partial responses when possible
   - Clear error messages

3. **Monitor and Adjust**
   - Regular review of rate limits
   - Analysis of usage patterns
   - User feedback incorporation

## Troubleshooting

### Common Issues

**"Rate limit exceeded" errors:**
1. Check current usage against limits
2. Verify request timing and batching
3. Consider upgrading to higher tier
4. Implement proper retry logic

**Inconsistent rate limiting:**
1. Check for multiple client instances
2. Verify user authentication
3. Review caching strategies
4. Check clock synchronization

**Performance issues:**
1. Monitor Redis performance
2. Review rate limiting algorithm
3. Check network latency
4. Optimize database queries

### Support

For rate limiting issues:
- **Documentation**: This guide and API reference
- **Status Page**: https://status.nimo-platform.com
- **Support Email**: support@nimo-platform.com
- **Developer Discord**: https://discord.gg/nimo-dev

---

**Last Updated**: August 2025  
**Version**: 1.0  
**Next Review**: September 2025