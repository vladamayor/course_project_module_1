import requests
from pprint import pprint
from datetime import datetime
import json


file = open ('token.txt', 'r')
token = file.readline().strip()
token_disk = file.readline()
file.close()


class VKUser:
    base_host = 'https://api.vk.com/'
    def __init__(self):
        pass
    
    def get_photos(self, id, album):
        uri = 'method/photos.get'
        URL = VKUser.base_host + uri
        get_photos_params = {
            'access_token': token,
            'v': '5.131',
            'owner_id': id,
            'album_id': album,
            'extended': '1',
            'photo_sizes': '1',
        }
        req = requests.get(URL, params=get_photos_params).json()
        return req['response']['items']

    def get_links(self, id, album):
        links_dic = {}
        info_upload = []
        likes_list = []
        info_photos = self.get_photos(id, album)
        for el in info_photos:
            file_upload = {}
            link = el['sizes'][-1]['url']
            likes = el['likes']['count']
            
            date = datetime.utcfromtimestamp(el['date']).strftime('%Y-%m-%d')
            if likes not in likes_list:
                links_dic[f'{likes}.jpg'] = link
                file_upload['file_name'] = f'{likes}.jpg'
            else:
                links_dic[f'{likes}_{date}.jpg'] = link
                file_upload['file_name'] = f'{likes}_{date}.jpg'

            file_upload['size'] = el['sizes'][-1]['type']
            info_upload.append(file_upload)
            likes_list.append(likes)
        print('Получены ссылки на скачивания файлов с VK')
        return links_dic, info_upload
    
    def sc_name(self, id):
        uri = 'method/utils.resolveScreenName'
        URL = VKUser.base_host + uri
        sc_params = {
            'access_token': token,
            'v': '5.131',
            'screen_name': id}
        req = requests.get(URL, params=sc_params).json()
        id = req['response']['object_id']
        return id


class Yandex:
    base_host = 'https://cloud-api.yandex.net/'

    def __init__(self, token_disk, id):
        self.token_disk = token_disk

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {token_disk}'
        }
    
    def _create_new_folder(self, id, album):
        uri = 'v1/disk/resources'
        requests_url = self.base_host + uri
        name_folder = f'/{album}_photo_id_{id}'
        params = {'path' : name_folder}
        response = requests.put(requests_url, params=params, headers=self.get_headers())
        if response.status_code == 201:
            print('Папка на Яндекс.Диск создана')
        else:
            print('Папка на Яндекс.Диск уже существует')
            
    def upload(self, id, album, el):
        uri = 'v1/disk/resources/upload'
        requests_url = self.base_host + uri
        yandex_path = f'/{album}_photo_id_{id}/{el[0]}'
        params = {'url': el[1], 'path': yandex_path}
        response = requests.post(requests_url, params=params, headers=self.get_headers())
        print(f'Файл {el[0]} успешно загружен по пути {yandex_path}')
        return response
        

class Upload(Yandex, VKUser):    
    def __init__(self, token_disk):
        pass
    
    def upload_to_disk(self, id, album, quantity):
        counter  = 0
        if type(id) == str:
            id = self.sc_name(id)
        self._create_new_folder(id, album)   
        links, info = self.get_links(id, album)
        for el in links.items():
            if counter < quantity:
                response = self.upload(id, album, el)
            counter += 1
        if response.status_code == 202:
            with open ('upload_info.json', 'w') as upload_info:
                json.dump(info, upload_info)
        else:
            print(response.json())


id = input('Введите id-пользователя или сокращенное имя: ')
print()
album = input('Введите тип альбома: wall — фотографии со стены, profile — фотографии профиля, saved — сохраненные фотографии: ')
print()
quantity = int(input('Введите количество загружаемых фото: '))
print()


if __name__ == '__main__':
    upload_user_photos = Upload(token_disk)
    upload_user_photos.upload_to_disk(id, album, quantity)