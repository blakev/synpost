import os
import re
import math
import string
from datetime import datetime

NAMABLES = string.ascii_letters + string.digits + '_- '

def clean_filename(s):
    s = ''.join([c for c in s if c in NAMABLES])
    s = re.sub(r'\W+', '_', s)
    return s

def path_to_asset(asset_obj):
    full_path = asset_obj.filepath
    upto_path = str(asset_obj.type).join(full_path.split(asset_obj.type)[1:])
    upto_path = asset_obj.type + ('/'.join(upto_path.strip(asset_obj.filename).split(os.path.sep)))
    return upto_path

def flatten_list(*args):
    return list([item for sublist in args for item in sublist])

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