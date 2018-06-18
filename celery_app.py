# -*- coding: utf-8 -*-
from celery import Celery
from settings import broker, backend


def connection(dct):
    return 'amqp://{user}:{password}@{ip}/{vhost}'.format(user=dct['user'], password=dct['password'], ip=dct['ip'],
                                                          vhost=dct['vhost'])

backend='rpc://'
broker='pyamqp://'

# backend = 'redis://localhost:6379'
# broker = 'redis://localhost:6379'

app = Celery(
    'vk_friends',
    broker=broker,
    backend=backend,
    include=['tasks'],

)



app.conf.update(
    CELERY_TIMEZONE='Europe/Moscow',
    CELERY_ENABLE_UTC=True,
    # CELERY_RESULT_BACKEND = 'rpc',
    # CELERY_RESULT_PERSISTENT = True,

    # CELERY_ACCEPT_CONTENT = ['pickle'],
    CELERYD_POOL = 'prefork',
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json', 'application/text'],

)

if __name__ == '__main__':
    app.start()