# -*- coding: utf-8 -*-

import time

class Waiter(object):
    '''
    Asynchronous Waiter class

    Execute a function with inter-execute time greater than 'delay'
    '''
    def __init__(self, delay, func, args, kwargs):
        super(Waiter, self).__init__()
        self.delay = delay
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._last_check_time = time.time()

    def run(self):
        cur_time = time.time()
        if cur_time - self._last_check_time >= self.delay: 
            self._last_check_time = cur_time
            self.func(*self.args, **self.kwargs)
