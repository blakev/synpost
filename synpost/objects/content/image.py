__author__ = 'Blake'

from basetypes import Asset

class Image(Asset):
    def __init__(self, obj, site = None):
        super(Image, self).__init__(obj, site)

    @property
    def mimetype(self):
        pass