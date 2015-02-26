__author__ = 'Blake'

from basetypes import TextContentAsset
from synpost.extensions import Category

class Article(TextContentAsset):
    def __init__(self, obj, site = None):
        super(Article, self).__init__(obj, site)

        Category.analyze(self)

    @property
    def extension(self):
        return 'html'