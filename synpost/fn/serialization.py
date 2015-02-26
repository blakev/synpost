import json

import types

class TupleEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, tuple):
            return str(obj)

        if not isinstance(obj, (str, list, set, dict, bool, types.NoneType)):
            if hasattr(obj, 'as_JSON'):
                return obj.as_JSON()
            elif hasattr(obj, 'to_JSON'):
                return obj.to_JSON()
            else:
                return str(obj)

        return json.JSONEncoder.default(self, obj)