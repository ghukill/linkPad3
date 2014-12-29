from localConfig import *

# Redis
BROKER_URL='redis://localhost:6379/{CELERY_BROKER}'.format(CELERY_BROKER=CELERY_BROKER)
RESULT_BACKEND='redis://localhost:6379/{CELERY_BACKEND}'.format(CELERY_BACKEND=CELERY_BACKEND)
RESULT_SERIALIZER='json'


