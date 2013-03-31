# -*- coding: utf-8 -*-

'''
Leaky Bucket Suite:
   * Single Leaky Bucket
   * Rate Limit Queue
   * Decorator to limit rate of any function
'''

class LeakyBucket(object):
    """Single Leaky Bucket

    Refs:

       * http://code.activestate.com/recipes/511490-implementation-of-the-token-bucket-algorithm/
    """
    def __init__(self, arg):
        super(LeakyBucket, self).__init__()
        self.arg = arg
        
class RateLimitQueue(object):
    """docstring for RateLimitQueue"""
    def __init__(self, arg):
        super(RateLimitQueue, self).__init__()
        self.arg = arg
        
def rate_limit(func):
    pass
