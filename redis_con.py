from redis import Redis

redis = Redis(
    # decode_responses=True,
    host='rs',
)
