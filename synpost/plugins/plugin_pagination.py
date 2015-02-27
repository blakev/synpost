__author__ = 'Blake'

from synpost.plugins.core import PluginCore

class PaginationPlugin(PluginCore):

    @staticmethod
    def execute(Action):
        print Action.site.ordered_articles

        return True
