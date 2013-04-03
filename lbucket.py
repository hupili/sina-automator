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
            ok = True
            for (b, q) in t.buckets.items():
                if self._buckets[b].tokens < q:
                    ok = False
                    break
            if ok:
                map(lambda x: self._buckets[x[0]].consume(x[1]), t.buckets.items())
                ret = t.execute()
            else:
                _new_tasks.append(t)
        self._tasks = _new_tasks

    def clear_tasks(self):
        self._tasks = []

    def get_buckets_info(self):
        ret = {}
        for (name, bucket) in self._buckets.items():
            ret[name] = {}
            ret[name]['max'] = bucket.capacity
            ret[name]['current'] = bucket.tokens
            ret[name]['rate'] = bucket.fill_rate
        return ret


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
            try:
                return fn(ret)
            except Exception as e:
                # Ignore callback failures
                print e
                pass
        else:
            return ret


from functools import wraps

def rate_limit(attr_rlq='rlq', buckets={}, callback=None):
    '''Decorate a rate limited function with callback function.
    It can only be used to decorate an object method and the object should
    have a RateLimitQueue field indicated by the name ``attr_rlq``.

    Note:

       * ``getattr(self, attr_rlq)`` should return a 
         RateLimitQueue object.
       * As a side effect, a ``callback`` kwarg will be added
         to the decorated function.

    :type attr_rlq: str
    :type buckets: dict

    :param attr_rlq: 
        The field name of RateLimitQueue

    :param buckets: 
        Specify how much resource the decorated function consumes at each invokation

    :param callback:
        Specify the default callback function for this decorated method. 
        It can be overrided by ``callback`` kwarg when calling the decorated method.
    '''
    def wrapper_rate_limit(func):
        @wraps(func)
        def wrapped_func(self, *args, **kwargs):
            import copy
            import inspect
            
            if 'callback' in kwargs and not 'callback' in inspect.getargspec(func).args:
                _cb = kwargs['callback']
                del kwargs['callback']
            else:
                _cb = callback
            q = getattr(self, attr_rlq)
            t = RLQTask(func, (self, ) + args, kwargs, copy.deepcopy(buckets), _cb)
            q.add_task(t)
            return None
        return wrapped_func
    return wrapper_rate_limit
