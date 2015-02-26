__author__ = 'Blake'

def load_from_list(objs_list, ToAssetType, site = None):
    for f in objs_list:
        yield ToAssetType(f, site)