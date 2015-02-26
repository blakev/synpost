__author__ = 'Blake'

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
