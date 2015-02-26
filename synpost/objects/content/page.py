__author__ = 'Blake'

from jinja2 import Template

from basetypes import TextContentAsset

class Page(TextContentAsset):
    def __init__(self, obj, site = None):
        super(Page, self).__init__(obj, site)

    @property
    def extension(self):
        return 'html'

    @property
    def as_HTML(self):
        template = Template(self.extracted_data.get('content', ''))
        template = template.render(**self.jinja_obj)
        return template