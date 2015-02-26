__author__ = 'Blake'

from basetypes import TextContentAsset, Category

class Article(TextContentAsset):
    def __init__(self, obj, site = None):
        super(Article, self).__init__(obj, site)

        self.metadata = self.generate_metadata(
            categories = Category.analyze(self)
        )

    @property
    def extension(self):
        return 'html'