__author__ = 'Blake'

from synpost.plugins.core import SitePluginCore

class PaginationSitePlugin(SitePluginCore):
    priority = 50
    action = 'site'

    @staticmethod
    def execute(Site):
        site = Site
        return site
