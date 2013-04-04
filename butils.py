# -*- coding: utf-8 -*-

'''
Bot Utils
'''

def get_followers(uid, cursor):
    if not '_get_followers' in data:
        data['_get_followers'] = []
    wa.get_followers(uid, cursor=cursor, callback=lambda x: data['_get_followers'].extend(x['users']))

from extraction.userext import user_extract
from extraction.urlext import url_extract
