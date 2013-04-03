# -*- coding: utf-8 -*-

from wauto import WeiboAutomator

FN_WORKSPACE = 'workingspace.pickle'

wa = WeiboAutomator()

def _load():
    try:
        with open(FN_WORKSPACE) as fp:
            wa.loads(fp.read())
    except:
        pass

def _save():
    with open(FN_WORKSPACE, 'w') as fp:
        fp.write(wa.dumps())

_load()
import atexit
atexit.register(_save)

if __name__ == '__main__':
    pass
