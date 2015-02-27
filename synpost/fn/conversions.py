import os
import re
import math
import string
import collections
from datetime import datetime

NAMABLES = string.ascii_letters + string.digits + '_- '


def flatten_list(*somelist):
    """ Takes one or more lists of lists and returns a single list
    >>> flatten_list([1,2,3,4])
    [1, 2, 3, 4]

    >>> flatten_list([[1,2],[3,4]])
    [1, 2, 3, 4]

    >>> flatten_list(None)
    Traceback (most recent call last):
        ...
    TypeError: 'NoneType' object is not iterable

    >>> flatten_list([])
    []

    >>> flatten_list('blake')
    ['b', 'l', 'a', 'k', 'e']

    >>> flatten_list([[1],[[2],[3]],[4,5,6],7])
    [1, 2, 3, 4, 5, 6, 7]

    >>> flatten_list([[1],[[2],[3]],[4,5,6],[7]])
    [1, 2, 3, 4, 5, 6, 7]

    """
    def flatten(x):
        for element in x:
            if isinstance(element, collections.Iterable) and not isinstance(element, basestring):
                for sub_element in flatten(element):
                    yield sub_element
            else:
                yield element

    if not somelist:
        return []

    return list(flatten([list(flatten(x)) for x in somelist]))

def merge_dicts(*dicts):
    """ Takes N number of dicts and updates them to the left-most dict

    >>> merge_dicts({})
    {}
    >>> merge_dicts({}, {})
    {}
    >>> merge_dicts({'a': 1}, {'b': 2})
    {'a': 1, 'b': 2}
    >>> merge_dicts({'a': 1}, {})
    {'a': 1}
    >>> merge_dicts({'a': {'a': 1}}, {'a': {'b': 2}})
    {'a': {'b': 2}}
    >>> merge_dicts(None)
    {}
    """
    def merge(a, b):
        z = a.copy()
        z.update(b)
        return z
    x = {}
    for d in dicts:
        if not d:
            d = {}
        x = merge(x, d)
    return x




def clean_filename(s):
    s = ''.join([c for c in s if c in NAMABLES])
    s = re.sub(r'\W+', '_', s)
    return s


def path_to_asset(asset_obj):
    full_path = asset_obj.filepath
    upto_path = str(asset_obj.type).join(full_path.split(asset_obj.type)[1:])
    upto_path = asset_obj.type + ('/'.join(upto_path.strip(asset_obj.filename).split(os.path.sep)))
    return upto_path



def convert_sysdate(ordinal, format):
    if format is None:
        format = '%B %d, %Y'

    # A FLOAT IS REQUIRED derp derp
    ordinal = float(ordinal)
    dt = datetime.fromtimestamp(ordinal)

    return dt.strftime(format)


def pretty_size(int_bytes, units = 1024):
    unit_str = 'KMGTP'

    if int_bytes < units:
        return '%d bytes' % int_bytes

    exp = int(math.log(int_bytes) / math.log(units))

    return '%0.2f %siB' % (int_bytes / math.pow(units, exp), unit_str[exp-1])


def size_from_pretty(str_size):
    # remove all the whitespaces
    s = re.sub(r'\s+', '', str_size)
    # lowercase everything for simplicity
    s = s.lower()

    num = re.findall(r'\d+\.?\d*', s)

    if len(num) == 1:
        num = int(float(num[0]))

    byte_mul = {
        'k': 1024,
        'm': 1024 * 1024,
        'g': 1024 * 1024 * 1024,
        't': 1024 * 1024 * 1024 * 1024
    }

    for size, mul in byte_mul.items():
        if size in s:
            num = num * mul

    return num


if __name__ == '__main__':
    import doctest
    doctest.testmod()