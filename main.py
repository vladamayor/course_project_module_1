import requests
from pprint import pprint
from datetime import datetime


file = open ('token.txt', 'r')
token = file.readline().strip()
token_disk = file.readline()
file.close()


class VKUser:
    URL = 'https://api.vk.com/method/photos.get'
    def __init__(self):
        pass
    
    def get_photos(self, id, album):
        get_photos_params = {
            'access_token': token,
            'v': '5.131',
            'owner_id': id,
            'album_id': album,
            'extended': '1',
            'photo_sizes': '1',
        }
        req = requests.get(VKUser.URL, params=get_photos_params).json()
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
        

class Upload(Yandex, VKUser):    
    def __init__(self, token_disk):
        pass
    
    def upload_to_disk(self, id, album): 
        self._create_new_folder(id, album)   
        links, info = self.get_links(id, album)
        uri = 'v1/disk/resources/upload'
        requests_url = self.base_host + uri
        for el in links.items():
            yandex_path = f'/{album}_photo_id_{id}/{el[0]}'
            print(f'Файл {el[0]} успешно загружен по пути {yandex_path}')
            params = {'url': el[1], 'path': yandex_path}
            response = requests.post(requests_url, params=params, headers=self.get_headers())
        if response.status_code == 202:
            print()
            pprint(info)
        else:
            print(response.json())


if __name__ == '__main__':
    upload_user_photos = Upload(token_disk)
    upload_user_photos.upload_to_disk()