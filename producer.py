#- * - coding: utf - 8 -*-
from tasks import deep_friends
from datetime import datetime
from celery import group
from settings import my_id, deep, m_friends_dct, d_friends_dct
from lib import request_url, friends, parts, save_or_load, groups_user
import time
import networkx
import random


parts = lambda lst, n: (lst[i:i + n] for i in iter(range(0, len(lst), n)))

def db_conn():
    pass
    # return postgresql.open('pq://eax@localhost/eax')


def cleaner(dct):
    """
	удаляем все заблокированные или удаленные анкеты
	"""
    return {k: v for k, v in dct.items() if v != None}


def get_friends(lst):
    d_friends = group(deep_friends.s(i) for i in parts(lst, 65))().get()
    result = {k: v for d in d_friends for k, v in d.items()}
    return result


def getMutual():
    all_friends = friends(my_id)
    c_friends = group(mutual_friends.s(i) for i in parts(list(all_friends[0].keys()), 75))().get()
    result = {k: v for d in c_friends for k, v in d.items()}
    return cleaner(result)


def getDeep(deep, start_id):
    result = {}
    for i in range(deep):
        if result:
            # те айди, которых нет в ключах + не берем id:None

            friends_1_circle = [val for val in result.values()]
            # friends_2_circle = [person['id']
            #                     for friend in friends_1_circle
            #                         for person in friend['items']
            #                             if 'deactivated' not in list(person.keys())]

            friends_2_circle = [person
                                for friend in friends_1_circle
                                    for person in friend['items']
                                        ]

            lst = list(set(friends_2_circle) - set(result.keys()))

            print(lst)
            print('{} circle, friends {}'.format(i, len(lst)))

            result = get_friends(lst)
            result.update(result)
        else:
            graph = {}
            all_friends = friends(start_id)

            print('0 circle, friends ', len(all_friends))
            lst = [person['id']
                   for person in all_friends.values()
                   if 'deactivated' not in list(person.keys())]
            result = get_friends(lst)
            result.update(result)

            #print(lst)
            #print('end list')
            #print(all_friends)
            #print((result['675069']))
            for friend_id in all_friends:
                # print(f'Processing{len(graph)} id: ', friend_id)
                graph[friend_id] = result[str(friend_id)]
            #[print(key) for key, val in graph.items()]
            g = networkx.Graph(directed=False)
            for i in graph:
                g.add_node(i, label=all_friends[i]['last_name'] + " " + all_friends[i]['first_name'],
                           sname=all_friends[i]['last_name'])
                if ('photo_200' in all_friends[i].keys()):
                    g.nodes(data=True)[i]['photo'] = all_friends[i]['photo_200']
                else:
                    g.nodes[i]['photo'] = "https://pp.userapi.com/c633518/v633518288/f4d7/SQDITLiix-M.jpg"
                g.nodes[i]['name'] = all_friends[i]['first_name']
                g.nodes[i]['gender'] = all_friends[i]['sex']
                if ('city' in all_friends[i].keys()):
                    g.nodes[i]['city_id'] = all_friends[i]['city']['id']
                else:
                    g.nodes[i]['city_id'] = 0
                g.nodes[i]['count_friends'] = result[str(i)]['count']
                g.nodes[i]['gender'] = all_friends[i]['sex']
                g.nodes[i]['viz'] = {'size': 54}
                g.nodes[i]['viz']['position'] = {'x': random.randint(0, 100), 'y': random.randint(0, 100), 'z': 0}
                g.nodes[i]['viz']['color'] = {'r': 255, 'g': 0, 'b': 0, 'a': 0}
                for j in graph[i]['items']:
                    if i != j and i in all_friends and j in all_friends:
                        g.add_edge(i, j)
                        # g.edges[i][j]['viz']['color'] = {'r': 1, 'g': 1, 'b': 1}

            # networkx.draw_networkx(g, pos, cmap=plt.get_cmap('jet'), node_size=50, with_labels=False)

            #print(g.nodes[11815387].keys())
            #print(g.nodes[11815387])
            networkx.write_gexf(g, "graph_%s.gexf"  % start_id, version="1.2draft")

    return cleaner(result)



def getDeepGroups(deep, start_id):
    result = {}
    for i in range(deep):
        if result:
            # те айди, которых нет в ключах + не берем id:None

            friends_1_circle = [val for val in result.values()]
            # friends_2_circle = [person['id']
            #                     for friend in friends_1_circle
            #                         for person in friend['items']
            #                             if 'deactivated' not in list(person.keys())]

            friends_2_circle = [person
                                for friend in friends_1_circle
                                    for person in friend['items']
                                        ]

            lst = list(set(friends_2_circle) - set(result.keys()))

            print(lst)
            print('{} circle, friends {}'.format(i, len(lst)))

            result = get_friends(lst)
            result.update(result)
        else:
            graph = {}
            all_friends = groups_user(start_id)
            print('0 circle, friends ', len(all_friends))
            lst = [person['id']
                   for person in all_friends.values()
                   if 'deactivated' not in list(person.keys())]
            result = get_friends(lst)
            result.update(result)

            #print(lst)
            #print(all_friends)
            #print(result['675069'])
            for friend_id in all_friends:
                # print(f'Processing{len(graph)} id: ', friend_id)
                graph[friend_id] = result[str(friend_id)]
            g = networkx.Graph(directed=False)
            for i in graph:
                g.add_node(i, label=all_friends[i]['last_name'] + " " + all_friends[i]['first_name'],
                           sname=all_friends[i]['last_name'])
                if ('photo_200' in all_friends[i].keys()):
                    g.nodes(data=True)[i]['photo'] = all_friends[i]['photo_200']
                else:
                    g.nodes[i]['photo'] = "https://pp.userapi.com/c633518/v633518288/f4d7/SQDITLiix-M.jpg"
                g.nodes[i]['name'] = all_friends[i]['first_name']
                g.nodes[i]['gender'] = all_friends[i]['sex']
                if ('city' in all_friends[i].keys()):
                    g.nodes[i]['city_id'] = all_friends[i]['city']['id']
                else:
                    g.nodes[i]['city_id'] = 0
                g.nodes[i]['viz'] = {'size': 54}
                g.nodes[i]['viz']['position'] = {'x': random.randint(0, 100), 'y': random.randint(0, 100), 'z': 0}
                g.nodes[i]['viz']['color'] = {'r': 255, 'g': 0, 'b': 0, 'a': 0}
                for j in graph[i]['items']:
                    if i != j and i in all_friends and j in all_friends:
                        g.add_edge(i, j)
                        # g.edges[i][j]['viz']['color'] = {'r': 1, 'g': 1, 'b': 1}

            # networkx.draw_networkx(g, pos, cmap=plt.get_cmap('jet'), node_size=50, with_labels=False)

            #print(g.nodes[11815387].keys())
            #print(g.nodes[11815387])
            networkx.write_gexf(g, "graph_groups%s.gexf" % start_id, version="1.2draft")

    return cleaner(result)



# def get_friends(deep, ids, uid):

#     result = {}
#     for id in ids:
#         result[id] = getDeep(deep, id)

#     # запись в базу.
#     with db_conn() as db:
#         update = db.prepare(
#             "UPDATE query SET response = $2, dt_end = $3, state=$4 WHERE uid = $1")
#         (_, cnt) = update(uid, result, datetime.now(), 'complete')

def multiporocess_func(id_target):
    friends = getDeep(2, id_target)
    print(sum( [ val['count'] for key, val in friends.items() ]))

if __name__ == '__main__':
    import time
    start_time = time.time()

    from multiprocessing import Pool
    from multiprocessing.dummy import Pool as ThreadPool

    #pool = ThreadPool(4)
    #pool = Pool(4)
    #pool.map(multiporocess_func, [200953551])#, 26461154,23175745, 11252538, 83798922, 34449127, 13369989])
    #pool.close()
    #pool.join()

    #friends = getDeep(2, 23175745)

    #friends = getDeep(1, 342670668)
    #friends = getDeep(1, 25941324)#anny
    #friends = getDeep(1, 86071988)

    #friends = getDeep(1, 196972616)#Slavyn
    friends = getDeepGroups(1, 'podslushano_dubna')

    print([val['count'] for key, val in friends.items()])
    print(sum([val['count'] for key, val in friends.items()]))


    # ---------------------------------
    # import vk_api
    # # # from vk_api.execute import VkFunction
    # #
    # token = '3a7a4220d52a6c4f1cac028a591fbc0eae47541a80d446f3c44161d8ad4e13e5397e51bc87318682e7d93'
    # vk_session = vk_api.VkApi(token=token)
    # all_friends = friends(200953551)
    # print('0 circle, friends ', len(all_friends))
    #
    # lst = [person['id']
    #        for person in all_friends.values()
    #        if 'deactivated' not in list(person.keys())]
    #
    #
    # with vk_api.VkRequestsPool(vk_session) as pool:
    #     friends = pool.method_one_param(
    #         'friends.get',  # Метод
    #         key='user_id',  # Изменяющийся параметр
    #         values=lst,
    #         # Параметры, которые будут в каждом запросе
    #         # default_values={'fields': 'domain'}
    #     )
    # friends = friends.result
    # friends_1_circle = [val for val in friends.values()]
    # friends_2_circle = [person
    #                     for friend in friends_1_circle
    #                     for person in friend['items']
    #                     ]
    #
    # lst = list(set(friends_2_circle) - set(friends.keys()))
    # print('{} circle, friends {}'.format(1, len(lst)))
    #
    # with vk_api.VkRequestsPool(vk_session) as pool:
    #     friends = pool.method_one_param(
    #         'friends.get',  # Метод
    #         key='user_id',  # Изменяющийся параметр
    #         values=lst,
    #         # Параметры, которые будут в каждом запросе
    #         # default_values={'fields': 'domain'}
    #     )
    #
    # friends = friends.result
    # print(sum( [ val['count'] for key, val in friends.items() ]))


    # ---------------------------------

    
    print("--- %s seconds ---" % (time.time() - start_time))


