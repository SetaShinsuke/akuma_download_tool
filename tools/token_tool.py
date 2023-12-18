import orjson as orjson
import requests
from common.browser_info import UA

API_BM_IMG_TOKEN = "https://manga.bilibili.com/twirp/comic.v1.Comic/ImageToken?device=pc&platform=web"


class TokenTool:

    def __init__(self, _type='bm'):
        self.type = _type
        self.headers = {
            'user-agent': UA
        }

    def get_tokened_urls(self, _pics, _headers = None):
        if _headers:
            self.headers.update(_headers)
        urls = []
        payloads = {
            "urls": orjson.dumps(_pics).decode()
        }
        rep = requests.post(API_BM_IMG_TOKEN, data=payloads, headers=_headers)
        if rep.ok:
            i = 1
            dataJson = rep.json()['data']
            for item in dataJson:
                urls.append(f'{item["url"]}?token={item["token"]}')
        else:
            raise Exception(f"Get token fail!\n{rep}")
        return urls
