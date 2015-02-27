__author__ = 'Blake'

import types
import json

def merge(o):
    if isinstance(o, dict):
        pass
    elif isinstance(o, str):
        o = json.loads(o)
    elif isinstance(o, types.FileType):
        o = json.load(o)
    else:
        raise ValueError('Unexpected type %s' % type(o))
    return dict(config_values.items() + o.items())


config_values = {
    "site_name": "My Default Site",
    "meta_delimeter": "$$",
    "project_source": "./TEST_ENV",
    "project_destination": "./TEST_ENV/build",
    "allow_folder_creation": True,
    "subfolder_as_category": True,
    "default_category": "default",
    # will copy all the generated files in /pages into / (like index.html)
    "page_files_in_root": True,
    # will copy ALL the generated files in /pages, including files that overwrite theme assets
    "assets_as_pages": False,
    # asset file names that are not part of synpost.objects.theme.Theme.REQUIRED_PIECES
    "additional_page_assets": ['contacts.html'],
    # them to use when generating the static site
    "theme": "default",
    "date_format": "%B %d, %Y",
    "pagination": 5,
    "output_format": "html5",
    "meta": {
        "me": "Blake VandeMerwe"
    }
}

