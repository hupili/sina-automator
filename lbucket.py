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
    def __init__(self, tokens_max, tokens_init, fill_rate):
        '''
        :type tokens_max: float
        :type tokens_init: float
        :type fill_rate: float
        :param fill_rate: unit: tokens/second
        '''
        super(LeakyBucket, self).__init__()
        import time
        self.time = time.time
        self.capacity = float(tokens_max)
        self._tokens = float(tokens_init)
        self.fill_rate = float(fill_rate)
        self.last_fill_time = self.time()

    def consume(self, tokens):
        """Consume tokens from the bucket. Returns True if there were
        sufficient tokens otherwise False."""
        if tokens <= self.tokens:
            self._tokens -= tokens
        else:
            return False
        return True

    def get_tokens(self):
        now = self.time()
        if self._tokens < self.capacity:
            delta = self.fill_rate * (now - self.last_fill_time)
            self._tokens = min(self.capacity, self._tokens + delta)
            self.last_fill_time = now
        return self._tokens

    tokens = property(get_tokens)

class RateLimitQueue(object):
    """docstring for RateLimitQueue"""
    def __init__(self):
        super(RateLimitQueue, self).__init__()
        self._buckets = {}
        self._tasks = []

    def add_bucket(self, name, bucket):
        '''
        :type name: str
        :type bucket: LeakyBucket
        '''
        self._buckets[name] = bucket

    def add_task(self, task):
        '''
        :type task: RLQTask
        '''
        self._tasks.append(task)

    def run(self):
        _new_tasks = []
        for t in self._tasks:
            for (b, q) in t.buckets.items():
                if self._buckets[b].consume(q):
                    del t.buckets[b]
            if len(t.buckets) == 0:
                ret = t.execute()
            else:
                _new_tasks.append(t)
        self._tasks = _new_tasks

    def clear_tasks(self):
        self._tasks = []

class RLQTask(object):
    """docstring for RLQTask"""
    def __init__(self, func, args, kwargs, buckets, callback=None):
        super(RLQTask, self).__init__()
        self.func = func
        self.args = args 
        self.kwargs = kwargs
        self.buckets = buckets
        self.callback = callback

    def execute(self):
        ret = None
        try:
            ret = self.func(*self.args, **self.kwargs)
        except Exception as e:
            ret = e
        if self.callback:
            fn = getattr(self, 'callback')
            return fn(ret)
        else:
            return ret

def rate_limit(func):
    pass
