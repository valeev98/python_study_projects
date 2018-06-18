# -*- coding: utf-8 -*-
import collections
import requests
import vk_api
from vk_api.audio import VkAudio


def main():
    import time
    start_time = time.time()
    """ Пример составления топа исполнителей для профиля вк """

    login, password = '+79876267637', 'dom4088093'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return


    #tok = 'e7f58f6f518f881010ac59905851c9d0d6a5722a0669ce0e1af3bb8e611392497d386df245d16dbb8c55f'
    #vk_session = vk_api.VkApi(token=tok, app_id=6240100)


    vkaudio = VkAudio(vk_session)

    artists = collections.Counter()

    offset = 0
    urls = []
    while True:
        audios = vkaudio.get(owner_id=86071988, offset=offset)

        if not audios:
            break

        for audio in audios:
            artists[audio['artist']] += 1
            urls.append({audio['url']: (audio['artist'] + ' - ' + audio['title'])[0:120].replace('/','')})
            #urls = set(urls)
        offset += len(audios)

    count = len(urls)
    for i in urls:
        for k, v in i.items():
            ufr = requests.get(k, stream=True)  # делаем запрос
            if ufr.status_code == 200:
                with open(('music/'+ v + '.mp3'), 'wb') as f:
                    f.write(ufr.content)
            else:
                print('Error')
    print('time: ' + str(time.time() - start_time) + ' count: ' + str(count))

if __name__ == '__main__':
    main()