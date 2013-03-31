# -*- coding: utf-8 -*-

import sys
sys.path.append('snsaspi')
import snsapi
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger
from lbucket import *

class WeiboAutomator(object):
    '''Wrap common operations with rate limit facility
    '''
    def __init__(self):
        super(WeiboAutomator, self).__init__()
        self.sp = SNSPocket()
        self.sp.load_config()
        self.sp.auth()
        # assign 'channel_name' as automator
        self.weibo = self.sp['automator'] 

        # Most buckets are derived from Sina's offcial description [1]. 
        # The additional one 'wauto_snsapi' limits SNSAPI request rate globally
        # (avoid lower layer failure). 
        # 
        # Ref:
        #    * [1] http://open.weibo.com/wiki/Rate-limiting
        sina_buckets = [
                ('wauto_snsapi', LeakyBucket(1, 1, 1)),
                ('ip.hour.test_auth', self.cal_bucket(1000, 60*60)),
                ('user.hour.test_auth.total', self.cal_bucket(150, 60*60)),
                ('user.hour.test_auth.update', self.cal_bucket(30, 60*60)),
                ('user.hour.test_auth.reply', self.cal_bucket(60, 60*60)),
                ('user.hour.test_auth.follow', self.cal_bucket(60, 60*60)),
                ('user.day.test_auth.follow', self.cal_bucket(100, 60*60*24)),
                ]
        self.rlq = RateLimitQueue() 
        map(lambda t: self.rlq.add_bucket(t[0], t[1]), sina_buckets)

    def cal_bucket(self, upperbound, period):
        '''
        Do conservative calculation to generate a bucket for SinaWeibo

        The limit is represented as ``x/y`` in the doc. 

        :param upperbound: x (in original scale)
        :param period: y (in seconds)
        '''
        # for safety
        ratio_capacity = 0.8
        ratio_init = 0.1
        upperbound = float(upperbound)
        period = float(period)
        fill_rate = upperbound / period
        tokens_max = upperbound * 0.8
        tokens_init = upperbound * 0.1
        return LeakyBucket(tokens_max, tokens_init, fill_rate)

    def run(self):
        return self.rlq.run()


    def follow(self, uid):
        ret = self.weibo.weibo_request('friendships/create',
                'POST',
                {'uid': uid})
        return ret

    def follow_by_name(self, screen_name):
        ret = self.weibo.weibo_request('friendships/create',
                'POST',
                {'screen_name': screen_name})
        return ret

    def home_timeline(self, count=20):
        return self.weibo.home_timeline(count)

    def update(self, text):
        return self.weibo.update(text)

    def reply(self, status, text):
        if isinstance(status, snsapi.snstype.Message):
            statusID = status.ID
        else:
            statusID = status
        return self.weibo.reply(statusID, text)

    def forward(self, status, text):
        return self.weibo.forward(status, text)

    def domain_show(self, url):
        '''Lookup user by personal url. 
        We will match and remove common weibo prefix. 

        :param url:
            e.g. 'http://weibo.com/xiena' --> url='xiena'
        '''
        import re
        pattern = re.compile('^http:\/\/(www\.)?weibo.com\/')
        url = re.sub(pattern, '', url)
        ret = self.weibo.weibo_request('users/domain_show',
                'GET',
                {'domain': url})
        return ret


if __name__ == '__main__':
    from time import sleep
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    wa = WeiboAutomator()
    pp.pprint(wa.rlq.get_buckets_info())
    sleep(0.6)
    pp.pprint(wa.rlq.get_buckets_info())
