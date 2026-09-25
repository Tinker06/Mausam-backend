import time


cache = {}

CACHE_DURATION = 300


def get_cached(key: str):

    if key not in cache:
        print(f"Cache MISS → {key}")
        return None

    cached_data, timestamp = cache[key]

    if time.time() - timestamp > CACHE_DURATION:
        print(f"Cache EXPIRED → {key}")
        return None

    print(f"Cache HIT → {key}")

    return cached_data


def get_stale_cached(key: str):

    if key not in cache:
        print(f"STALE CACHE MISS → {key}")
        return None

    cached_data, timestamp = cache[key]

    print(f"STALE CACHE FOUND → {key}")

    return cached_data


def set_cached(key: str, data):

    cache[key] = (
        data,
        time.time()
    )

    print(f"Cache SET → {key}")