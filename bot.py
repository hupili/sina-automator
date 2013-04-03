# -*- coding: utf-8 -*-

# http://stackoverflow.com/questions/380870/python-single-instance-of-program
from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

from wauto import WeiboAutomator

FN_WORKSPACE = 'workingspace.pickle'

wa = WeiboAutomator()

def _load():
    try:
        with open(FN_WORKSPACE) as fp:
            wa.loads(fp.read())
    except IOError:
        pass

def _save():
    with open(FN_WORKSPACE, 'w') as fp:
        fp.write(wa.dumps())

_load()
import atexit
atexit.register(_save)

if __name__ == '__main__':
    from time import sleep
    #sleep(20)
    pass
