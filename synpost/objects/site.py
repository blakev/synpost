__author__ = 'Blake'

import os
import json

from synpost.fn.io import generic_collect
from synpost.fn.bootstrapping import load_from_list
from synpost.fn.serialization import TupleEncoder

from synpost.objects.theme import DefaultTheme, Theme
from synpost.objects.content import all_content_types

class EmptySite(object):
    def __init__(self, *args, **kwargs):
        self.config = {}
        self.theme = None
        self.collected_items = {}

    @property
    def all_items(self):
        return [item for itemtypes in self.collected_items.values() for item in itemtypes]

    @property
    def ordered_items(self):
        return sorted(self.all_items, key = lambda item: item.created, reverse = True)

    @property
    def ordered_articles(self):
        return filter(lambda x: x.type == 'articles', self.ordered_items)

    @property
    def all_pages(self):
        return filter(lambda x: x.type == 'pages', self.ordered_items)

    def article_index(self, article):
        return self.ordered_articles.index(article)


class Site(EmptySite):
    def __init__(self, config, theme = None):
        super(Site, self).__init__()

        self.config = config
        self.theme = DefaultTheme if not theme else theme

        if not isinstance(self.theme, Theme):
            raise ValueError('%s not of type synpost.objects.Theme' % type(self.theme))

        self.load_em = [
            ('pages', None),
            ('articles', None),
            ('images', [self.theme.get('images')]),
            ('scripts', [self.theme.get('scripts')]),
            ('styles', [self.theme.get('styles')])
        ]

        self.collected_items = self.__coerce()

        self.update_articles_with_num()


    def __repr__(self):
        return json.dumps(self.as_JSON(), indent = 4, cls = TupleEncoder)

    def as_JSON(self):
        return {self.config['site_name']: self.collected_items}

    def __collect(self, path, regex = None, ftype = None):
        if not ftype:
            ftype = path
        return generic_collect(os.path.join(self.config['project_source'], path), regex, ftype)

    def __coerce(self):
        collected_items = {}
        for content_type, appendit in self.load_em:
            if not appendit:
                appendit = []
            temp_files = self.__collect(content_type)
            for item in appendit:
                temp_files.extend(item)
            collected_items[content_type] = list(
                load_from_list(
                    temp_files, all_content_types[content_type], site = self
                )
            )
        return collected_items

    def update_articles_with_num(self):
        articles = self.ordered_articles
        for index, article in enumerate(articles):
            article.id_number = index + 1
            article.total_articles = len(articles)

    def compile(self):
        pass
