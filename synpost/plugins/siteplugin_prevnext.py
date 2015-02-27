__author__ = 'Blake'

from synpost.plugins.core import SitePluginCore



class AssetByUuidSitePlugin(SitePluginCore):
    priority = 50
    action = 'site'

    @staticmethod
    def execute(Site):
        if not Site.is_available('uuid_map'):
            return Site

        uuid_chain = {}

        for article in Site.ordered_articles:
            uuid_chain[article.uuid] = article.identifiers

        Site.set_from_plugin('uuid_map', uuid_chain)

        return Site




class PrevNextSitePlugin(SitePluginCore):
    priority = 100
    action = 'site'

    @staticmethod
    def execute(Site):
        from synpost.fn.helpers import sliding_window

        meta_attr = PrevNextSitePlugin.name # prevnext

        if not Site.is_available(meta_attr):
            return Site

        page_chain = {}

        for article in sliding_window([None, None] + Site.ordered_articles, 3):
            upnext, current, previous = article

            if current is None:
                continue

            page_chain[current.uuid] = { # create the <- previous / next -> chain
                'prev_article': previous.uuid if previous else None,
                'next_article': upnext.uuid if upnext else None
            }

        Site.set_from_plugin(meta_attr, page_chain)

        return Site
