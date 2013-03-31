# -*- coding: utf-8 -*-

from lbucket import LeakyBucket

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

if __name__ == '__main__':
    test_bucket()

