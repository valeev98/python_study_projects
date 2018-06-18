# -*- coding: utf-8 -*-
import requests
import random
from settings import token, api_v
import pickle

import vk_api

def request_url(method_name, parameters, access_token=False):
	"""read https://vk.com/dev/api_requests"""

	req_url = 'https://api.vk.com/method/{method_name}?{parameters}&v={api_v}'.format(
		method_name=method_name, api_v=api_v, parameters=parameters)

	if access_token:
		req_url = '{}&access_token={token}'.format(req_url, token=random.choice(token))

	return req_url

def friends(id):
	"""
	read https://vk.com/dev/friends.get
	Принимает идентификатор пользователя
	"""

	token = '3a7a4220d52a6c4f1cac028a591fbc0eae47541a80d446f3c44161d8ad4e13e5397e51bc87318682e7d93'
	vk_session = vk_api.VkApi( token=token)

	target = [id]
	with vk_api.VkRequestsPool(vk_session) as pool:
			friends_target = pool.method_one_param(
				'friends.get',  # Метод
				key='user_id',  # Изменяющийся параметр
				values=target,

				# Параметры, которые будут в каждом запросе
				default_values={'fields': 'domain,photo_200,sex,city'}
			)
	friends_target = friends_target.result[target[0]]
	# удаляем деактивированные анкеты
	friends_target["items"] = list(filter((lambda x: 'deactivated' not in x.keys()), friends_target['items']))
	friends_target = {item['id']: item for item in friends_target['items']}
	return friends_target

def groups_user(id):
	"""
	read https://vk.com/dev/friends.get
	Принимает идентификатор пользователя
	"""

	token = '3a7a4220d52a6c4f1cac028a591fbc0eae47541a80d446f3c44161d8ad4e13e5397e51bc87318682e7d93'
	vk_session = vk_api.VkApi(token=token)
	vk = vk_session.get_api()
	respons = vk.groups.getMembers(group_id = id)
	target = []
	for i in range(0,respons["count"],1000):
		target.append(i)


	with vk_api.VkRequestsPool(vk_session) as pool:
			friends_target = pool.method_one_param(
				'groups.getMembers',  # Метод
				key='offset',  # Изменяющийся параметр
				values=target,

				# Параметры, которые будут в каждом запросе
				default_values={'fields': 'domain,photo_200,sex', 'group_id':id}
			)

	#print(friends_target.result[1000])
	res = {"items":[]}
	for i in target:
		res["items"] += (friends_target.result[i]["items"])
	#print(res)
	# удаляем деактивированные анкеты
	res["items"] = list(filter((lambda x: 'deactivated' not in x.keys()), res['items']))
	res = {item['id']: item for item in res['items']}
	return res

def save_or_load(myfile, sv, smth=None):
	if sv and smth:
		pickle.dump(smth, open(myfile, "wb"))
	else:
		return pickle.load(open(myfile, "rb"))

parts = lambda lst, n: (lst[i:i + n] for i in iter(range(0, len(lst), n)))

make_targets = lambda lst: ",".join(str(x) for x in lst)