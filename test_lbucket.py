# -*- coding: utf-8 -*-

from lbucket import *

def test_bucket():
    from time import sleep
    bucket = LeakyBucket(80, 70, 10)
    print "tokens =", bucket.tokens
    print "consume(10) =", bucket.consume(8)
    print "consume(10) =", bucket.consume(1)
    sleep(1)
    print "tokens =", bucket.tokens
    sleep(1)
    print "tokens =", bucket.tokens
    print "consume(90) =", bucket.consume(90)
    print "tokens =", bucket.tokens

def _add_two_num(a, b):
    print "a =", a
    print "b =", b
    return a + b

def test_rlq_task():
    import sys
    # Normal function test
    t = RLQTask(lambda x: sys.stdout.write(x), ['test RQLTask output\n'], {}, {}, None)
    print t.execute()
    # Test other funcs
    t = RLQTask(_add_two_num, [1, 2], {}, {}, None)
    print t.execute()
    # Test mixed parameters
    t = RLQTask(_add_two_num, [1], {'b': 3}, {}, None)
    print t.execute()
    # Test all kw params
    t = RLQTask(_add_two_num, [], {'b': 3, 'a': 9}, {}, None)
    print t.execute()
    # Test callback
    t = RLQTask(_add_two_num, [], {'b': 5, 'a': 9}, {}, lambda x: sys.stdout.write("result = %s\n" % x))
    print t.execute()

if __name__ == '__main__':
    test_bucket()
    test_rlq_task()

