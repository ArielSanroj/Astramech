#!/usr/bin/env python3
"""
Intelligent rate limiter that adapts to X's behavior
"""

import asyncio
import time
import random
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class RequestType(Enum):
    SEARCH = "search"
    POST = "post"
    LOGIN = "login"

@dataclass
class RequestRecord:
    timestamp: float
    request_type: RequestType
    success: bool
    response_time: float
    error_code: int = None

class IntelligentRateLimiter:
    def __init__(self):
        self.requests: List[RequestRecord] = []
        self.base_delays = {
            RequestType.SEARCH: 2.0,
            RequestType.POST: 5.0,
            RequestType.LOGIN: 10.0
        }
        self.adaptive_delays = self.base_delays.copy()
        self.max_requests_per_minute = 10
        self.max_requests_per_hour = 50
        
    def record_request(self, request_type: RequestType, success: bool, response_time: float, error_code: int = None):
        """Record a request for analysis"""
        self.requests.append(RequestRecord(
            timestamp=time.time(),
            request_type=request_type,
            success=success,
            response_time=response_time,
            error_code=error_code
        ))
        
        # Keep only last 1000 requests
        if len(self.requests) > 1000:
            self.requests = self.requests[-1000:]
        
        # Update adaptive delays based on recent performance
        self._update_adaptive_delays()
    
    def _update_adaptive_delays(self):
        """Update delays based on recent request performance"""
        current_time = time.time()
        recent_requests = [r for r in self.requests if current_time - r.timestamp < 300]  # Last 5 minutes
        
        for request_type in RequestType:
            type_requests = [r for r in recent_requests if r.request_type == request_type]
            
            if len(type_requests) < 5:  # Not enough data
                continue
            
            success_rate = sum(1 for r in type_requests if r.success) / len(type_requests)
            avg_response_time = sum(r.response_time for r in type_requests) / len(type_requests)
            
            # Adjust delay based on success rate and response time
            if success_rate < 0.8:  # Low success rate
                self.adaptive_delays[request_type] *= 1.5
            elif success_rate > 0.95 and avg_response_time < 2.0:  # High success, fast response
                self.adaptive_delays[request_type] *= 0.8
            
            # Ensure delays stay within reasonable bounds
            self.adaptive_delays[request_type] = max(0.5, min(30.0, self.adaptive_delays[request_type]))
    
    async def wait_before_request(self, request_type: RequestType):
        """Wait before making a request based on intelligent rate limiting"""
        current_time = time.time()
        
        # Check if we're hitting rate limits
        recent_requests = [r for r in self.requests if current_time - r.timestamp < 60]  # Last minute
        hourly_requests = [r for r in self.requests if current_time - r.timestamp < 3600]  # Last hour
        
        if len(recent_requests) >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - recent_requests[0].timestamp)
            print(f"⏳ Rate limit: waiting {wait_time:.1f}s (minute limit)")
            await asyncio.sleep(wait_time)
        
        if len(hourly_requests) >= self.max_requests_per_hour:
            wait_time = 3600 - (current_time - hourly_requests[0].timestamp)
            print(f"⏳ Rate limit: waiting {wait_time:.1f}s (hourly limit)")
            await asyncio.sleep(wait_time)
        
        # Wait based on adaptive delay
        base_delay = self.adaptive_delays[request_type]
        
        # Add jitter to avoid synchronized requests
        jitter = random.uniform(0.5, 1.5)
        delay = base_delay * jitter
        
        print(f"⏳ Waiting {delay:.1f}s before {request_type.value} request")
        await asyncio.sleep(delay)
    
    def get_stats(self) -> Dict:
        """Get current rate limiting statistics"""
        current_time = time.time()
        recent_requests = [r for r in self.requests if current_time - r.timestamp < 300]  # Last 5 minutes
        
        stats = {
            "total_requests": len(self.requests),
            "recent_requests": len(recent_requests),
            "adaptive_delays": self.adaptive_delays.copy(),
            "success_rate": 0.0,
            "avg_response_time": 0.0
        }
        
        if recent_requests:
            stats["success_rate"] = sum(1 for r in recent_requests if r.success) / len(recent_requests)
            stats["avg_response_time"] = sum(r.response_time for r in recent_requests) / len(recent_requests)
        
        return stats

# Global rate limiter
rate_limiter = IntelligentRateLimiter()

async def test_rate_limiter():
    """Test the intelligent rate limiter"""
    print("🧪 Testing Intelligent Rate Limiter")
    print("=" * 40)
    
    # Simulate some requests
    for i in range(10):
        request_type = random.choice(list(RequestType))
        
        await rate_limiter.wait_before_request(request_type)
        
        # Simulate request
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate request time
        response_time = time.time() - start_time
        
        # Record request (simulate 90% success rate)
        success = random.random() < 0.9
        rate_limiter.record_request(request_type, success, response_time)
        
        print(f"Request {i+1}: {request_type.value} - {'✅' if success else '❌'} ({response_time:.2f}s)")
    
    # Show stats
    stats = rate_limiter.get_stats()
    print("\n📊 Rate Limiter Stats:")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Recent requests: {stats['recent_requests']}")
    print(f"Success rate: {stats['success_rate']:.2%}")
    print(f"Avg response time: {stats['avg_response_time']:.2f}s")
    print(f"Adaptive delays: {stats['adaptive_delays']}")

if __name__ == "__main__":
    asyncio.run(test_rate_limiter())