__author__ = 'Blake'

import os
import sys
import json
import argparse

import synpost
import synpost.default_config

from synpost.objects.site import Site
from synpost.objects.theme import Theme

DEFAULT_ACTIONS = {
    'build': synpost.build,
    # 'draft': synpost.draft,
    # 'hoist': synpost.hoist,
    # 'lint': synpost.lint,
}


def null_fn(*args, **kwargs):
    return True

def main(conf=None):
    if not conf:
        conf = {}

    # None, str, or type(Theme)
    theme = conf['namespace'].theme

    # if theme is a string try and load the specified theme
    # failure case will return None, which loads the default theme
    # style in Site.__init__(..)
    if isinstance(theme, str):
        theme = Theme.theme_from_name(theme)

    # create a new site with a config and a Theme object
    site = Site(conf, theme)

    return DEFAULT_ACTIONS[conf['namespace'].action](site).go()

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