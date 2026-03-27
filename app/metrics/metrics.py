from prometheus_client import Counter, Histogram

# 定义一个计数器，用于统计 API 调用次数
REQUEST_COUNTER = Counter(
    'api_requests_total', 
    'Total number of API requests'
    )

REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'Latency of API requests in seconds'
    )

CACHE_HIT = Counter(
    'cache_hits_total',
    'Total number of cache hits'
    )
CACHE_MISS = Counter(
    'cache_misses_total',
    'Total number of cache misses'
    )