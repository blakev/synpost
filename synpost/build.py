__author__ = 'Blake'

import os
import re
import json

from fn.io import create_folders_from_dict
from fn.io import collect_files_from

import objects.content as Content
from objects.action import Action

MARKDOWN_FILES = re.compile(r'[\s\S]+\.md', re.I)

required_folders = {
    'static': ['imgs', 'js', 'css', 'fonts'],
    'pages': []
}


class Build(Action):
    def __init__(self, site):
        self.description = 'BuildAction'
        self.config = site.config

        super(Build, self).__init__()

        self.dest_folder = self.config['project_destination']
        self.source_folder = self.config['project_source']

        self.site_config = self.get_blog_config_file()

    def go(self):
        self.verify_folders()



    def help(self):
        pass

    def get_blog_config_file(self):
        config_file = os.path.join(self.source_folder, 'config.json')

        if not os.path.exists(config_file):
            raise EnvironmentError('Cannot find %s' % config_file)

        try:
            return json.load(open(config_file, 'r'))
        except Exception, e:
            print e

        return {}

    def verify_folders(self):
        create_key = 'allow_folder_creation'
        can_create = self.config[create_key]

        if not os.path.exists(self.dest_folder):
            if can_create:
                os.makedirs(self.dest_folder)
            else:
                raise ValueError('%s does not exist, must set %s to "true"' % self.dest_folder, create_key)
        create_folders_from_dict(self.dest_folder, required_folders, overwrite = can_create)

    def __collect(self, subfolder, with_regex = None):
        from_folder = os.path.join(self.source_folder, subfolder)

        if not os.path.exists(from_folder) or not os.path.isdir(from_folder):
            raise EnvironmentError('Could not find folder %s' % from_folder)

        return list(
            collect_files_from(
                from_folder , with_regex
            )
        )

    def collect_articles(self):
        return []
        # kwargs = {
        #     'folder_categories': self.config['subfolder_as_category'],
        #     'project_config': self.config
        # }
        # return Content.article.parse_from_list(self.__collect('articles', MARKDOWN_FILES), **kwargs)

    def collect_static_assets(self):
        return self.__collect('static', MARKDOWN_FILES)

    def collect_templates(self):
        return self.__collect('templates', MARKDOWN_FILES)

    def collect_pages(self):
        return self.__collect('pages', MARKDOWN_FILES)

