__author__ = 'Blake'

from synpost.fn.helpers import min_max

class PluginMeta(type):
    def __new__(cls, name, parents, dct):
        if not 'plugin' in dct:
            dct['plugin'] = name.lower().strip('plugin')

        return super(PluginMeta, cls).__new__(cls, name, parents, dct)

class PluginCore(object):
    __metaclass__ = PluginMeta

    def __init__(self, Action, priority = None, explicit_step = None):
        self.Action = Action

        if priority:
            self.priority = min_max(0, 100, priority)

        if explicit_step:
            self.priority = self.priority_from_action(explicit_step)

        # if we didn't tell the plugin where it should run
        # in the `go` stack, we'll put it at the bottom
        if priority is None and explicit_step is None:
            self.priority = 100


    def priority_from_action(self, step):
        print self.Action.go_pipeline

        return 0
