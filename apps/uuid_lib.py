#!flask/bin/python
# -*- coding: UTF-8 -*

import time
import random
import string
from threading import Lock

lock = Lock()
uuid_info={}

def create_uuid(nexturl):
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    i=0

    while i < 15:
        sa.append(random.choice(seed))
        i+=1
    salt = ''.join(sa)

    lock.acquire()
    if salt in uuid_info:
        uuid = ''
    else:
        info={}
        info['authorized']=False
        info['time']=time.time()
        info['code']=None
        info['redirect_uri']=None
        info['user_id']=None
        uuid_info[salt]=info
        uuid=salt

    lock.release()
    return uuid

def get_uuid_auth_result(uuid):
    lock.acquire()
    resultinfo={}
    if uuid in uuid_info:
        # time_now=time.time()
        # expire=time_now-uuid_info[uuid]['time']
        # if expire > 300:
            # resultinfo=None
        # else:
        resultinfo['authorized']=uuid_info[uuid]['authorized']
        resultinfo['code']=uuid_info[uuid]['code']
        resultinfo['redirect_uri']=uuid_info[uuid]['redirect_uri']
        resultinfo['user_id'] = uuid_info[uuid]['user_id']
    else:
        resultinfo=None

    lock.release()
    return resultinfo

def set_uuid_true_url(uuid,true_url):
    lock.acquire()

    if uuid in uuid_info:
        uuid_info[uuid]['true_url']=true_url

    lock.release()

    return

def get_uuid_true_url(uuid):
    url=None
    lock.acquire()

    if uuid in uuid_info:
        url=uuid_info[uuid]['true_url']

    lock.release()
    return url


def set_uuid_pass_auth(uuid,code,redirect_uri,user_id):
    lock.acquire()

    if uuid in uuid_info:
        uuid_info[uuid]['code']=code
        uuid_info[uuid]['redirect_uri']=redirect_uri
        uuid_info[uuid]['authorized']=True
        uuid_info[uuid]['user_id'] = user_id

    lock.release()

    return

def delete_uuid(uuid):
    lock.acquire()

    if uuid in uuid_info:
        del uuid_info[uuid]

    lock.release()

    return
