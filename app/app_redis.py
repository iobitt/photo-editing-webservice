import redis as redis_module

redis = redis_module.Redis(host='redis', decode_responses=True)
