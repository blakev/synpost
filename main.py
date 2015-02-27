__author__ = 'Blake'

import os
import sys
import json
import argparse

import synpost
import synpost.default_config

# bootstrap the plugins that are installed
import synpost.plugins.enabled_plugins as plugins
from synpost.plugins.core import PluginCore, SitePluginCore

from synpost.objects.site import Site
from synpost.objects.theme import Theme

DEFAULT_ACTIONS = {
    'build': synpost.build,
    # 'draft': synpost.draft,
    # 'hoist': synpost.hoist,
    # 'lint': synpost.lint,
}

#
# returns the enabled_plugins for a given build action
#
def get_plugins_for_action(action, prefix = 'plugin'):
    return_plugins = []

    # get all the attributes in enabled_plugins that start with "something" (aka prefix)
    # the only values in there will be "plugin_*" or "__*__" variables
    usable_plugins = filter(lambda x: x.startswith(prefix), dir(plugins))

    # analyze each potential plugin we found in the namespace to see if there
    # is a matching object to go with it
    for poss_plugin in usable_plugins:
        # get the value stored at the possible_plugin from the enabled_plugins above
        plugin_cantidate = plugins.__dict__[poss_plugin]

        if not hasattr(plugin_cantidate, '__dict__'):
            continue

        # represents a file with potential plugin classes inside it
        plugin_class = plugin_cantidate.__dict__
        # find all the objects in that file that contain 'prefix'
        plugin_objs = filter(lambda x: prefix in x.lower(), plugin_class.keys())

        our_plugin_names = []

        for pot_plugin in plugin_objs:
            # bootstrap our potential plugin with the actual plugin class
            pot_plugin = plugin_class[pot_plugin]

            # invalid cantidate, no action attribute
            if not hasattr(pot_plugin, 'action'):
                continue
            else:
                # if the plugin's action matches our cmd action
                if pot_plugin.action == action:
                    # then keep it
                    our_plugin_names.append(pot_plugin)

        # extend our plugin list
        return_plugins.extend(our_plugin_names)

    # remove the plugin core objects that will be in EVERY action
    for remove_plugin in [PluginCore, SitePluginCore]:
        if remove_plugin in return_plugins:
            return_plugins.remove(remove_plugin)

    # let's do this!!
    return return_plugins

def null_fn(*args, **kwargs):
    return True

def main(conf=None):
    if not conf:
        conf = {}

    # what are we doing? comes from the command line
    do_action = conf['namespace'].action

    # None, str, or type(Theme)
    theme = conf['namespace'].theme

    # if theme is a string try and load the specified theme
    # failure case will return None, which loads the default theme
    # style in Site.__init__(..)
    if isinstance(theme, str):
        theme = Theme.theme_from_name(theme)

    # gather the pre-site built plugins
    site_plugins = get_plugins_for_action('site', prefix = 'siteplugin')

    # create a new site with a config and a Theme object
    site = Site(conf, theme, site_plugins)

    action_plugins = get_plugins_for_action(do_action)

    return DEFAULT_ACTIONS[do_action](site, action_plugins).go()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build a static site.')
    parser.add_argument('--config', type=str, default=None, action='store')
    parser.add_argument('--action', type=str, default='build', action='store')
    parser.add_argument('--theme', type=str, default=None, action='store')

    args = parser.parse_args()

    if args.action.lower() not in DEFAULT_ACTIONS.keys():
        raise ValueError('Unsupported operation %s' % args.action)

    # default configuration file
    if args.config is None:
        config = synpost.default_config.config_values

    else:
        with open(args.config, 'r') as ins_file:
            config = synpost.default_config.merge(ins_file)

    config['namespace'] = args

    status = main(config)

    print status