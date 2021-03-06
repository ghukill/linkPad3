from __future__ import absolute_import

from celery import Celery

# instantiate Celery object
celery = Celery(backend='redis://localhost:6379/1',include=[
                         'linkPad3.views'
                        ])

# import celery config file
celery.config_from_object('cl.celeryConfig')

if __name__ == '__main__':
    celery.start()
