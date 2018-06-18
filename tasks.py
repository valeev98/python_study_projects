# -*- coding: utf-8 -*-
from celery import Celery, bootsteps, Task
from celery_app import app
import requests
from settings import my_id
from lib import request_url, make_targets, parts

import vk_api

from celery.bin import Option


class APITask(Task):
    """API vk requests task class."""

    # the API authentication
    token = 'defoault_token'

class CustomArgs(bootsteps.Step):
    def __init__(self, worker, api_token, **options):
        # store the api authentication
        print('________ token 1 ________' ,api_token)
        APITask.token = api_token

app.user_options['worker'].add(
    Option('--token', dest='api_token', default=None, help='API token.') )
app.steps['worker'].add(CustomArgs)


@app.task(base=APITask, bind=True, token='token_temp',autoretry_for=(IOError,), retry_kwargs={'max_retries': 10})
def deep_friends(self, friends):
    import time
    start_time = time.time()
    print( 'friends number - ', len(friends))

    token = APITask.token
    vk_session = vk_api.VkApi(token=token)

    with vk_api.VkRequestsPool(vk_session) as pool:
        friends = pool.method_one_param(
            'friends.get',  # Метод
            key='user_id',  # Изменяющийся параметр
            values=friends,
            # Параметры, которые будут в каждом запросе
            # default_values={'fields': 'domain'}
        )
    print("--- %s seconds ---" % (time.time() - start_time))

    result = friends.result
    return result
