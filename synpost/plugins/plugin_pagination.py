__author__ = 'Blake'

from synpost.plugins.core import PluginCore

class PaginationPlugin(PluginCore):
    def __init__(self, Action, priority):
        super(PaginationPlugin, self).__init__(Action, priority)