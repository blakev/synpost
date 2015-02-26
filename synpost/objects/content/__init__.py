__author__ = 'Blake'

from basetypes import Asset, TextContentAsset

import article, page, image, script, style

all_content_types = {
    'pages': page.Page,
    'articles': article.Article,
    'images': image.Image,
    'scripts': script.Script,
    'styles': style.Style
}
