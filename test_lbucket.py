# -*- coding: utf-8 -*-

from lbucket import *
import sys
from time import sleep

def test_bucket():
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
    # Test Exception
    t = RLQTask(lambda: 1/0, [], {}, {}, lambda x: sys.stdout.write("result = %s\n" % x))
    print t.execute()

def _get_print_task(msg):
    return RLQTask(lambda: sys.stdout.write(msg + '\n'), [], {}, {}, None)

def test_rlq1():
    # Basic looping for tasks
    q = RateLimitQueue()
    q.add_task(_get_print_task('T 1'))
    q.add_task(_get_print_task('T 2'))
    q.add_task(_get_print_task('T 3'))
    print "q.run()" 
    q.run()
    print "q.run()" 
    q.run()

def _get_print_task_with_limit(msg, value):
    return RLQTask(lambda: sys.stdout.write(msg + '\n'), 
            [], {}, {'quota': value}, 
            lambda x: sys.stdout.write('execute done: %s\n' % msg))

def test_rlq2():
    # Rate limit test
    b = LeakyBucket(20, 10, 5)
    q = RateLimitQueue()
    q.add_bucket('quota', b)
    q.add_task(_get_print_task_with_limit('T 1', 1))
    q.add_task(_get_print_task_with_limit('T 2', 2))
    q.add_task(_get_print_task_with_limit('T 10', 10))
    print "q.run()"
    q.run()
    print "sleep 2 seconds"
    sleep(2)
    print "q.run()"
    q.run()
    print "q.run()"
    q.run()

class RateLimitedClass(object):
    """docstring for RateLimitedClass"""
    def __init__(self):
        super(RateLimitedClass, self).__init__()
        self.rlq = RateLimitQueue()
        self.rlq.add_bucket('quota', LeakyBucket(10, 3, 2))
        self.count = 0
    
    @rate_limit(buckets={'quota': 2}) 
    def do(self):
        self.count += 1
        print "I'm doing: %s" % self.count

    @rate_limit(buckets={'quota': 2}, callback=lambda x: sys.stdout.write('ret=%s\n' % x))
    def cal(self, a, b):
        return _add_two_num(a, b)

def test_rlq_rate_limit():
    c = RateLimitedClass()
    c.do()
    c.do()
    c.do()
    print c.rlq.get_buckets_info()
    #print c.rlq._buckets
    #print c.rlq._tasks
    print 'RLQ run'
    print c.rlq.run()
    print c.rlq.get_buckets_info()
    print 'RLQ run'
    print c.rlq.run()
    print 'Sleep 2'
    sleep(2)
    print 'RLQ run'
    print c.rlq.run()

def test_rlq_rate_limit2():
    c = RateLimitedClass()
    c.cal(1, 2)
    c.cal(3, 2)
    c.cal(3, 9)
    print c.rlq.get_buckets_info()
    print 'RLQ run'
    print c.rlq.run()
    print c.rlq.get_buckets_info()
    print 'RLQ run'
    print c.rlq.run()
    print 'Sleep 2'
    sleep(2)
    print 'RLQ run'
    print c.rlq.run()

if __name__ == '__main__':
    #test_bucket()
    #test_rlq_task()
    #test_rlq1()
    #test_rlq2()
    #test_rlq_rate_limit()
    test_rlq_rate_limit2()

