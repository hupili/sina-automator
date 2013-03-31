# -*- coding: utf-8 -*-

import sys
sys.path.append('snsaspi')
import snsapi
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger

class WeiboAutomator(object):
    """docstring for WeiboAutomator"""
    def __init__(self):
        super(WeiboAutomator, self).__init__()
        self.sp = SNSPocket()
        self.sp.load_config()
        self.sp.auth()
        # assign 'channel_name' as automator
        self.b = self.sp['automator'] 

    def follow(self, uid):
        ret = b.weibo_request('friendships/create',
                'POST',
                {'uid': uid})
        return ret

if __name__ == '__main__':
    pass
