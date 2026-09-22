import time


# Store cached data here
cache = {}

# Cache duration: 5 minutes
CACHE_DURATION = 300


def get_cached(key: str):
    if key not in cache:
        print(f"Cache MISS → {key}")
        return None

    cached_data, timestamp = cache[key]

    # Check whether cache has expired
    if time.time() - timestamp > CACHE_DURATION:
        print(f"Cache EXPIRED → {key}")
        del cache[key]
        return None

    print(f"Cache HIT → {key}")
    return cached_data


def set_cached(key: str, data):
    cache[key] = (data, time.time())
    print(f"Cache SET → {key}")