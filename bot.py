# -*- coding: utf-8 -*-

# http://stackoverflow.com/questions/380870/python-single-instance-of-program
from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import dill

from wauto import WeiboAutomator
from queue import Queue

FN_WORKSPACE = 'workingspace.bin'

def _input(x):
    q.input(x)

def _load():
    global wa, q, data
    try:
        with open(FN_WORKSPACE) as fp:
            _workspace = dill.loads(fp.read())
            # To store any user data
            data = _workspace['data']
            wa = _workspace['wa']
            q = _workspace['q']
            q.connect()
    except IOError:
        data = {}
        wa = WeiboAutomator()
        q = Queue('message.db')
        q.connect()

def _save():
    with open(FN_WORKSPACE, 'w') as fp:
        _workspace = {'data': data, 'wa': wa, 'q': q}
        fp.write(dill.dumps(_workspace))

_load()
import atexit
atexit.register(_save)

if __name__ == '__main__':
    from time import sleep
    import pprint
    wa.run()
    print "Left tasks:", len(wa.rlq._tasks)
    pprint.pprint(wa.rlq.get_buckets_info())
