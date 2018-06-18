#- * - coding: utf - 8 -*-
from tasks import deep_friends
from datetime import datetime
from celery import group
from settings import my_id, deep, m_friends_dct, d_friends_dct
from lib import request_url, friends, parts, save_or_load
import time
import networkx
import random
# -*- coding: utf-8 -*-
import collections

import vk_api
from vk_api.audio import VkAudio


def main():
    """ Пример составления топа исполнителей для профиля вк """

    token = '9b4ffeade1110fe81a1aea05edb7dff5bfa149fb5d12d69e7a51b846ad0067b704111bab468f6c8d94d71'
    vk_session = vk_api.VkApi(token=token, app_id=6369427)

    vkaudio = VkAudio(vk_session)

    artists = collections.Counter()

    offset = 0

    while True:
        audios = vkaudio.get(owner_id=86071988, offset=offset)

        if not audios:
            break

        for audio in audios:
            artists[audio['artist']] += 1

        offset += len(audios)

    # Составляем рейтинг первых 15
    print('\nTop 15:')
    for artist, tracks in artists.most_common(15):
        print('{} - {} tracks'.format(artist, tracks))

    # Ищем треки самого популярного
    most_common_artist = artists.most_common(1)[0][0]

    print('\nSearch for', most_common_artist)

    tracks = vkaudio.search(q=most_common_artist)[:10]

    for n, track in enumerate(tracks, 1):
        print('{}. {} {}'.format(n, track['title'], track['url']))

if __name__ == '__main__':
    main()