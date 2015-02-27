__author__ = 'Blake'

from itertools import tee, izip_longest

def min_max(mi, ma, val):
    """Returns the value inside a min and max range
    >>> min_max(0, 100, 50)
    50
    >>> min_max(0, 100, -1)
    0
    >>> min_max(0, 100, 150)
    100
    >>> min_max(0, 0, 0)
    0
    >>> min_max(0, 1, 0)
    0
    >>> min_max(0, 0, 1)
    0
    """
    return max(mi, min(ma, val))

def sliding_window(seq, size = 3):
    iters = tee(seq, size)
    for i in xrange(1, size):
        for each in iters[i:]:
            next(each, None)
    return izip_longest(*iters, fillvalue=None)
