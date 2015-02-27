__author__ = 'Blake'

from jinja2 import Template

from basetypes import TextContentAsset
from synpost.extensions import Category

class Article(TextContentAsset):
    theme_piece = 'article.html'

    def __init__(self, obj, site = None):
        super(Article, self).__init__(obj, site)

        Category.analyze(self)

    @property
    def extension(self):
        return 'html'

    @property
    def finalized_html(self):
        Piece = self.site.theme.asset_by_filename('pieces', self.theme_piece)
        template = self.site.theme.jinja_environment.get_template(Piece.filename)
        template = template.render(rendered_content = self.as_HTML, **self.jinja_obj)
        return template
