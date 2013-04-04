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

def _ana_user(message):
    ul = user_extract(message.parsed.text)['users']
    return ul

def ana_users(message_list):
    '''
    Both Message or MessageList are supported
    '''
    if isinstance(message_list, list):
        ul = map(_ana_user, message_list)
        return reduce(lambda a,b: a + b, ul, [])
    else:
        return _ana_user(message_list)
