__author__ = 'Blake'

from basetypes import Asset

class Style(Asset):
    def __init__(self, obj, site = None):
        super(Style, self).__init__(obj, site)

    @property
    def mimetype(self):
        return 'text/css'

    @property
    def as_HTML(self):
        return self._mirror_contents()