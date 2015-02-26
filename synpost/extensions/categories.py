__author__ = 'Blake'

import os

from synpost.extensions.metaextension import MetaExtension

# root folders/categories for all items to go inside
STATIC_CATEGORIES = ['articles', 'pages']

class Category(MetaExtension):
    def __init__(self, asset, attribute):
        super(Category, self).__init__(asset, attribute)

    @staticmethod
    def category_from_path(p, base_path = None):
        drive, parts = os.path.splitdrive(p)

        if not base_path:
            pass
        else:
            # remove the source base directory from the path;
            parts = parts.split(base_path)[-1]
            # split the filename from the folders in front of it
            # get all of the pieces except the filename on the end
            parts = parts.split(os.path.sep)[:-1]
            # clean up the seperator junk
            parts = [x.lower() for x in parts if x != '']
            # TEST_ENV/articles/cars/red/redcar vroom.md => ['cars', 'red']
            return [p for p in parts if p not in STATIC_CATEGORIES]

    @staticmethod
    def analyze(asset):
        # add the folder path leading up to the root of the project
        # as category types to the article/page/asset
        if asset.site.config.get('folder_as_categories', True):
            path_categories = Category.category_from_path(asset.path, asset.site.config.get('project_source', '.'))
        else:
            path_categories = []

        # combine the methods of category analysis
        c = asset.metadata.get('categories', []) + path_categories

        # filter the categories so they're all lowercase
        c = map(lambda x: x.lower(), c)

        MetaExtension.overwrite_values('categories', asset, c)

        return c

