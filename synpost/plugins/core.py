__author__ = 'Blake'
import copy

from functools import partial
from synpost.fn.helpers import min_max

class PluginMeta(type):
    def __new__(cls, name, parents, dct):
        if not 'name' in dct:
            dct['name'] = name.lower().replace('plugin', '').replace('site', '')

        if not 'action' in dct:
            dct['action'] = 'build'

        if not 'priority' in dct:
            dct['priority'] = 100

        return super(PluginMeta, cls).__new__(cls, name, parents, dct)

    def __call__(cls, Action):
        a = copy.copy(Action)
        return partial(cls.execute, a)

    def __str__(cls):
        return 'plugin-%s' % cls.plugin


class PluginCore(object):
    __metaclass__ = PluginMeta

    plugin = 'core'
    action = 'core'
    priority = -1

    def __init__(self, Action):
        self.go_fn = partial(self.execute, Action)

    @staticmethod
    def execute(Action):
        raise NotImplementedError
        # return True/False



class SitePluginCore(PluginCore):
    __metaclass__ = PluginMeta

    plugin = 'site_core'
    action = 'site'
    priority = -1

    def __init__(self, Site):
        super(SitePluginCore, self).__init__(Site)

    @staticmethod
    def execute(Site):
        raise NotImplementedError
        # return Site
