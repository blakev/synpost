__author__ = 'Blake'

from synpost.plugins.core import PluginMeta as PluginType

class Action(object):
    def __init__(self, plugins = None, pipeline = None):

        if not plugins:
            plugins = []

        if not pipeline:
            pipeline = []

        self.description = 'DefaultAction'
        self.go_pipeline = pipeline
        self.plugins = plugins

        self.insert_plugins_to_pipeline()

    def help(self):
        raise NotImplementedError

    def go(self):
        results = []
        for fn in self.go_pipeline:
            results.append(fn())
        return results

    def go_pipeline_names(self):
        return map(lambda func: func.__name__, self.go_pipeline)

    def insert_plugins_to_pipeline(self):
        if not self.plugins:
            return

        # sorted plugins by priority for pipeline insertion
        sorted_plugins = sorted(self.plugins, key=lambda x: x.priority)

        for index, fn in enumerate(self.go_pipeline):
            if sorted_plugins:
                top_plugin = sorted_plugins[0]
                if not isinstance(top_plugin, PluginType):
                    raise ValueError('%s not of type<PluginType>' % top_plugin)

            score = int((float(index) / len(self.go_pipeline)) * 100)

            if top_plugin.priority <= score:
                init_plugin = sorted_plugins.pop(0)(self)
                self.go_pipeline.insert(index, init_plugin)

        # extend the remaining (>last score and <100) to the pipeline
        self.go_pipeline.extend(map(lambda x: x(self), sorted_plugins))


    def __str__(self):
        return self.description

    def __repr__(self):
        return self.__str__