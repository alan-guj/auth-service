# -*- coding:utf-8 -*-
import json,requests
from resources import IMG_SERVICE_URI
# USER_URI= 'http://120.27.150.13:6053/api/v1.0/users'
# REGISTRATION_URI = 'http://120.27.150.13:6053/api/v1.0/registration'
class ImgApi:
    img_baseurl = IMG_SERVICE_URI
    headers = {'content-type':'application/json'}

    _oauth_client = None
    system_token = None

    def __init__(self,oauth_client=None):
        self._oauth_client = oauth_client

    def get_system_token(self):
        resp = requests.get(self._oauth_client.base_url+self._oauth_client.access_token_url,
                params = {'grant_type':'client_credentials',
                    'client_id':self._oauth_client.consumer_key,
                    'client_secret':self._oauth_client.consumer_secret})
        self.system_token = resp.json().get('access_token')


    def get_img(self, img_url):
        if(img_url is None or img_url == ''):
            return None
        if(self.system_token is None):
            self.get_system_token()
        url = self.img_baseurl
        payload = {
            'medialist':[
                {
                    'positiontype':'oss',
                    'position':img_url,
                }
            ]
        }

        r=self._oauth_client.post(url,content_type='application/json',
                                    token={'access_token':self.system_token},
                                      data=json.dumps(payload))
        if r.status == 401 or r.status == 403:
            self.get_system_token()
            return self.get_img()
        if r.status < 200 or r.status >= 300:
            return None
        if not r.data or not 'medialist' in r.data :
            return None
        return r.data['medialist'][0]['accessurl']

