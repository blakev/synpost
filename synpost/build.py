__author__ = 'Blake'

import os
import re
import json
import shutil

import synpost.globals as GLOBALS

import synpost.objects.content as Content
from synpost.objects.action import Action
from synpost.fn.io import collect_files_from, create_folders_from_dict
from synpost.fn.conversions import path_to_asset

MARKDOWN_FILES = re.compile(r'[\s\S]+\.md', re.I)

required_folders = {
    'static': ['imgs', 'js', 'css', 'fonts'],
    'pages': [],
    'articles': []
}

content_locations = {
    'articles': ['articles'],
    'pages': ['pages'],
    'styles': ['static', 'css'],
    'scripts': ['static', 'js'],
    'images': ['static', 'imgs']
}

class Build(Action):
    def __init__(self, site, plugins = None):
        if not plugins:
            plugins = []

        self.site = site

        if self.site.plugins:
            self.site = self.site.go()

        self.description = 'BuildAction'
        self.config = site.config

        self.dest_folder = self.config['project_destination']
        self.source_folder = self.config['project_source']

        pipeline = [
            self.delete_old_folders,
            self.create_new_folders,
            self.copy_static_assets,
            self.build_dynamic_assets,
            self.copy_index
        ]

        super(Build, self).__init__(plugins, pipeline)


    def delete_old_folders(self):
        try:
            shutil.rmtree(self.dest_folder)
            os.makedirs(self.dest_folder)
        except Exception, e:
            return e
        else:
            return True


    def create_new_folders(self):
        # create the folder tree
        try:
            create_folders_from_dict(self.dest_folder, required_folders, True)
        except Exception, e:
            return e
        else:
            return True

    def __static_assets(self, is_static = True):
        return filter(lambda x: x.is_static == is_static, self.site.all_items)

    def copy_static_assets(self):
        for item in self.__static_assets(True):
            # get the new path relative to destination folder
            path_prefix = list(content_locations[item.type])
            # affix the original filename to the end of the path
            path_prefix.append(item.filename)
            # insert the project destination (build dir) to the front
            path_prefix.insert(0, self.dest_folder)
            # join the whole path together
            new_path = os.path.join(*path_prefix)
            # copy the original file into the new path we just created
            shutil.copy2(item.path, new_path)
        return True

    def build_dynamic_assets(self):
        for item in self.__static_assets(False):
            # extract path and new file name
            npath, nname = os.path.split(item.href.strip('/'))
            # append new folder path with project destination (build dir)
            if item.type == 'pages':
                new_path = os.path.join(self.dest_folder, 'pages')
            else:
                new_path = os.path.join(self.dest_folder, npath)

            # create the path to the folder
            if not os.path.exists(new_path):
                os.makedirs(new_path)

            with open(os.path.join(new_path, nname), 'w') as out_file:
                out_file.write(item.finalized_html)
        return True

    def copy_index(self):
        index_path = os.path.join(self.dest_folder, 'pages', 'index.html')

        if not os.path.exists(index_path):
            with open(os.path.join(self.dest_folder, 'index.html'), 'w') as out_file:
                out_file.writelines(GLOBALS.DEFAULT_INDEX_HTML)
        else:
            shutil.copy2(index_path, self.dest_folder)

        return True
