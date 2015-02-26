__author__ = 'Blake'

from basetypes import Asset

class Script(Asset):
    def __init__(self, obj, site = None):
        super(Script, self).__init__(obj, site)

    @property
    def mimetype(self):
        return 'text/javascript'

    @property
    def as_HTML(self):
        return self._mirror_contents()