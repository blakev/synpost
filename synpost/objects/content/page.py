__author__ = 'Blake'

from basetypes import TextContentAsset

class Page(TextContentAsset):
    def __init__(self, obj, site = None):
        super(Page, self).__init__(obj, site)

    @property
    def extension(self):
        return 'html'