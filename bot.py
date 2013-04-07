# -*- coding: utf-8 -*-

# http://stackoverflow.com/questions/380870/python-single-instance-of-program
from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import dill

from wauto import WeiboAutomator
from queue import Queue
from waiter import Waiter

FN_WORKSPACE = 'workingspace.bin'

def _load():
    global wa, q, data, w
    try:
        with open(FN_WORKSPACE) as fp:
            _workspace = dill.loads(fp.read())
            # To store any user data
            data = _workspace['data']
            wa = _workspace['wa']
            q = _workspace['q']
            q.connect()
            w = _workspace['w']
    except IOError:
        data = {}
        wa = WeiboAutomator()
        q = Queue('message.db')
        q.connect()
        w_timeline = Waiter(200, wa.home_timeline, (), 
                {'count': 100, 'callback': q.input})
        w = [w_timeline]

def _save():
    with open(FN_WORKSPACE, 'w') as fp:
        _workspace = {'data': data, 'wa': wa, 'q': q, 'w': w}
        fp.write(dill.dumps(_workspace))

def _run_regular_job():
    for j in w:
        j.run()

_load()
import atexit
atexit.register(_save)

import butils
import sys
_bu = sys.modules['butils']
setattr(_bu, 'wa', wa)
setattr(_bu, 'w', w)
setattr(_bu, 'q', q)
setattr(_bu, 'data', data)
from butils import *

_run_regular_job()

if __name__ == '__main__':
    cmd_fns = sys.argv[1:]
    for fn in cmd_fns:
        #butils.cmd_from_file(fn)
        execfile(fn)
    from time import sleep
    import pprint
    wa.run()
    print "Left tasks:", len(wa.rlq._tasks)
    pprint.pprint(wa.rlq.get_buckets_info())
