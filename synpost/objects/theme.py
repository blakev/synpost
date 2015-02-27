__author__ = 'Blake'

import os
import re
from collections import namedtuple

from jinja2 import Environment as JinjaEnvironment, FileSystemLoader as JinjaLoader

from synpost.fn.io import generic_collect

ThemeFile = namedtuple('ThemeFile', 'filename valiname filepath extension type')
Valifile = namedtuple('ValiFile', 'valiname type')

# default themes folder, look for other themes IN HERE; by name and path
theme_folder = os.path.join(os.getcwd(), 'synpost', 'themes')

class Theme(object):
    REQUIRED_PIECES = ['article', 'footer', 'header', 'main', 'sidebar']
    REQUIRED_STYLES = ['main']
    REQUIRED_SCRIPTS = []

    pieces_regex = re.compile(r'[\s\S]+\.(html|htm|jinja|txt)', re.I)
    styles_regex = re.compile(r'[\s\S]+\.(css|less|sass)', re.I)
    scripts_regex = re.compile(r'[\s\S]+\.(js|coffee)', re.I)
    images_regex = re.compile(r'[\s\S]+\.(gif|png|jpg)', re.I)

    def __init__(self, name, at_path):
        self.name = name
        self.path = at_path

        self.collection_points = {
            'pieces': (os.path.join(self.path, 'pieces'), Theme.pieces_regex),
            'styles': (os.path.join(self.path, 'assets', 'css'), Theme.styles_regex),
            'scripts': (os.path.join(self.path, 'assets', 'js'), Theme.scripts_regex),
            'images': (os.path.join(self.path, 'assets', 'img'), Theme.images_regex)
        }

        self.collected_items = {}

        for ftype, identity in self.collection_points.items():
            self.collected_items[ftype] = generic_collect(identity[0], identity[1], ftype, ThemeFile)

        self.jinja_environment = self.collection_points['pieces'][0] # path the pieces folder
        self.jinja_environment = JinjaEnvironment(loader=JinjaLoader(self.jinja_environment), cache_size=500)

    def get(self, object_type):
        objects = self.collected_items.get(object_type.lower(), None)
        return [] if not objects else objects


    def asset_by_filename(self, asset_type, filename):
        asset_collection = self.collected_items.get(asset_type.lower(), self.collection_points['pieces'])
        candidates = filter(lambda theme_file: theme_file.filename.lower() == filename.lower(), asset_collection)
        if not candidates:
            return None
        else: return candidates[0]


    def validated(self):
        our_set = self.validation_set
        default_set = DefaultTheme.validation_set
        return default_set.issubset(our_set)

    @property
    def validation_set(self):
        theme_file_set = set()
        for theme_file in [item for sublist in self.collected_items.values() for item in sublist]:
            theme_file_set.add(Valifile(theme_file.valiname, theme_file.type))
        return theme_file_set

    @staticmethod
    def find_themes():
        return filter(lambda x: os.path.isdir(os.path.join(theme_folder, x)), os.listdir(theme_folder))


    @staticmethod
    def theme_from_folder(path):
        if not os.path.isdir(path):
            raise ValueError('%s is not a valid path' % path)

        # take the supplied path, split it on the OS seperator; either \ or /
        # then, take the last element which is our starting folder
        name = path.split(os.path.sep)[-1]
        return Theme(name, path)

    @staticmethod
    def theme_from_name(name):
        if name not in Theme.find_themes():
            name = 'default'
        return Theme.theme_from_folder(os.path.join(theme_folder, name))


DefaultTheme = Theme.theme_from_name('default')
MinimalTheme = Theme.theme_from_name('minimal')
