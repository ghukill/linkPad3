import redis
from localConfig import IMAGE_DB

# redis handle
r_thumbs = redis.StrictRedis(host='localhost', port=6379, db=IMAGE_DB)
