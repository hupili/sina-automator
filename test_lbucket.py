# -*- coding: utf-8 -*-

from lbucket import LeakyBucket

if __name__ == '__main__':
    from time import sleep
    bucket = LeakyBucket(80, 60, 1)
    print "tokens =", bucket.tokens
    print "consume(10) =", bucket.consume(10)
    print "consume(10) =", bucket.consume(10)
    sleep(1)
    print "tokens =", bucket.tokens
    sleep(1)
    print "tokens =", bucket.tokens
    print "consume(90) =", bucket.consume(90)
    print "tokens =", bucket.tokens

