__author__ = 'Blake'

import os
import json

from synpost.fn.io import generic_collect
from synpost.fn.bootstrapping import load_from_list
from synpost.fn.serialization import TupleEncoder

from synpost.plugins.core import PluginMeta as PluginType
from synpost.objects.theme import DefaultTheme, Theme
from synpost.objects.content import all_content_types

class EmptySite(object):
    def __init__(self, *args, **kwargs):
        self.config = {}
        self.theme = None
        self.site_items = {}
        self.metadata = {}

        self.plugins = kwargs.get('plugins', [])
        self.go_pipeline = kwargs.get('pipeline', [])

        self.insert_plugins_to_pipeline()

    def go(self):
        results = self
        for plugin in self.go_pipeline:
            results = plugin(results)()
        return results

    def insert_plugins_to_pipeline(self):
        # taken from synpost.objects.action.Action fn insert_plugins_to_pipeline
        sorted_plugins = sorted(self.plugins, key=lambda x: x.priority)
        for index, fn in enumerate(self.go_pipeline):
            if sorted_plugins:
                top_plugin = sorted_plugins[0]
                if not isinstance(top_plugin, PluginType):
                    raise ValueError('%s not of type<PluginType>')
            score = int((float(index) / len(self.go_pipeline)) * 100)
            if top_plugin.priority <= score:
                self.go_pipeline.insert(index, sorted_plugins.pop(0))
        self.go_pipeline.extend(sorted_plugins)

    @property
    def all_items(self):
        return [item for itemtypes in self.site_items.values() for item in itemtypes]

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
    def __init__(self, config, theme = None, plugins = []):
        super(Site, self).__init__(plugins = plugins)

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

        self.site_items = self.__coerce()

        self.update_articles_with_num()


    def __repr__(self):
        return str(self.site_items)

    def as_JSON(self):
        return {self.config['site_name']: self.site_items}

    def __collect(self, path, regex = None, ftype = None):
        if not ftype:
            ftype = path
        return generic_collect(os.path.join(self.config['project_source'], path), regex, ftype)

    def __coerce(self):
        site_items = {}
        for content_type, appendit in self.load_em:
            if not appendit:
                appendit = []
            temp_files = self.__collect(content_type)
            for item in appendit:
                temp_files.extend(item)
            site_items[content_type] = list(
                load_from_list(
                    temp_files, all_content_types[content_type], site = self
                )
            )
        return site_items

    def update_articles_with_num(self):
        articles = self.ordered_articles
        for index, article in enumerate(articles):
            article.id_number = index + 1
            article.total_articles = len(articles)

    def compile(self):
        pass
