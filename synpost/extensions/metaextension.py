import types

from synpost.fn.conversions import merge_dicts

class MetaExtension(object):
    def __init__(self, asset, attribute):
        self.asset = asset
        self.attribute = attribute

    @staticmethod
    def analyze(asset):
        raise NotImplementedError

    @staticmethod
    def extend_values(attribute, asset, new_values):
        n = new_values
        original_value = asset.metadata.get(attribute, None)

        # null or not present
        if original_value is None:
            if attribute not in asset.metadata.keys():
                asset.metadata[attribute] = new_values
            else:
                asset.metadata[attribute] = [None, new_values]
            return

        # not a container, put in a list (str, int, float, null)
        if not isinstance(original_value, (list, dict)):
            asset.metadata[attribute] = [original_value]

        # original value is a dictionary object, update with new
        # values overwriting the old values if new values are also
        # a dictionary, otherwise add the new values as a key under
        # the dictionary with the new values set
        elif isinstance(original_value, dict):
            if isinstance(n, dict):
                asset.metadata[attribute] = merge_dicts(original_value, n)
            else:
                asset.metadata[attribute][attribute] = n
            return

        if isinstance(n, (str, int, float, types.NoneType)): # append
            asset.metadata[attribute].append(n)
        elif isinstance(n, list): # extend
            asset.metadata[attribute].extend(n)
        else:
            raise ValueError('WTF did you pass me?? %s' % new_values)


    @staticmethod
    def overwrite_values(attribute, asset, new_values):
        asset.metadata[attribute] = new_values
