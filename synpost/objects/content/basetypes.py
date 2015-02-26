__author__ = 'Blake'

import os
import re
import json
import time
import mimetypes

import markdown
import yaml
from jinja2 import Template

from synpost.fn.conversions import pretty_size, convert_sysdate, \
    flatten_list, path_to_asset

# root folders/categories for all items to go inside
STATIC_CATEGORIES = ['articles', 'pages']

# bootstrap mimetypes table with MARKDOWN extension
mimetypes.types_map['.md'] = 'text/plain'

import synpost.objects

class Asset(object):
    def __init__(self, asset_obj, site = None):
        # initialize with a site's shell if we don't give it one
        # this will allow functions that rely on the site's properties
        # to continue working without being broken
        self.site = synpost.objects.site.EmptySite() if not site else site

        # the asset_obj is a namedtuple of type ThemeFile or SiteFile (interop)
        self.asset = asset_obj

        self.path = asset_obj.filepath      # full file path
        self.filename = asset_obj.filename  # filename with extension
        self.ext = asset_obj.extension      # extension only
        self._type = asset_obj.type         # synthetic Asset type
        self.meta = {}                      # default meta data about the file

        self.metadata = self.default_meta_extraction()

    def default_meta_extraction(self):
        stats = os.stat(self.path)
        meta = {
            'filename': self.filename,
            'valiname': self.asset.valiname,
            'created': {
                'ctime': stats.st_ctime,
                'pretty': convert_sysdate(stats.st_ctime, self.site.config.get('date_format', None))
            },
            'last_edited': {
                'ctime': stats.st_mtime,
                'pretty': convert_sysdate(stats.st_mtime, self.site.config.get('date_format', None))
            },
            'filesize': {
                'bytes': stats.st_size,
                'pretty': pretty_size(stats.st_size)
            }
        }
        return meta

    @property
    def href(self):
        cleans = {
            'type': self.type.lower(),
            'date': convert_sysdate(self.metadata['created']['ctime'], '%Y/%m/%d'),
            'name': self.shortname,
            'extension': self.extension or self.ext.strip('.')
        }

        return '{type}/{date}/{name}.{extension}'.format(**cleans)

    @property
    def identifiers(self):
        meta = self.metadata
        the_year = convert_sysdate(meta['created']['ctime'], '%Y')
        return [
            '%s-%s' % (the_year, hex(int(meta['created']['ctime']) & 0xffffff).split('x')[1]),
            self.shortname,
            path_to_asset(self.asset) + self.shortname,
            self.href
        ]


    @property
    def type(self):
        return self._type

    @property
    def mimetype(self):
        return mimetypes.guess_type(self.path, strict = False)

    @property
    def extension(self):
        return None # Implemented in the child types

    @property
    def shortname(self):
        return '_'.join([c.lower() for c in self.metadata.get('title', self.asset.valiname).split()])[:30].strip('_')

    def to_JSON(self):
        return json.dumps(self.name, default=lambda x: x.__dict__, sort_keys=True)

    def as_JSON(self):
        return self.__dict__

    def _mirror_contents(self):
        with open(self.path, 'r') as ins_file:
            lines = ins_file.readlines()
        return ''.join(lines)

    def __repr__(self):
        return self.to_JSON()

    def __str__(self):
        return '<Asset.%s filename: %s>' % (self.type.capitalize(), str(self.filename))


class TextContentAsset(Asset):
    metadata_regex = re.compile(r'(\$\$\n+(.*\n)*?\$\$)', re.I)
    whitespace_regex = re.compile(r'\w+', re.I + re.M)

    def __init__(self, asset_obj, site = None):
        super(TextContentAsset, self).__init__(asset_obj, site)

        with open(self.path, 'r') as ins_file:
            content_lines = ins_file.readlines()

        # get the content and the meta data blocks from the text file
        extracted = self.__extract(content_lines)

        self.extracted_data = {
            'meta': extracted[0], 'content': extracted[1]
        }

    def __preprocess_meta(self, meta_block):
        template = Template(meta_block)
        return template.render(**self.site.config.get('meta', {}))

    def __extract(self, content_lines):
        meta_stack = []         # lines inside the $$ allocated as meta-data
        content_stack = []      # article content lines
        feeding_meta = False    # are we currently in a meta-data block? yes/no
        meta_blocks = 0         # meta-data block delimeters encountered; needs to be equal

        for line in content_lines:
            if line.startswith(self.site.config.get('meta_delimeter', '$$')):
                meta_blocks += 1
                feeding_meta = not feeding_meta
                continue

            if not feeding_meta:
                content_stack.append(line)
            else:
                meta_stack.append(line)

        if meta_blocks % 2 != 0:
            raise SyntaxError('%s contains an invalid number of meta-data block delimeters' % self.filename)

        meta_block = '\n'.join([m.strip() for m in meta_stack if m.strip() != ''])
        content_block = '\n'.join([c.strip() for c in content_stack])

        return (
            self.extract_meta_data(self.__preprocess_meta(meta_block)) or {},
            content_block or ''
        )

    def generate_metadata(self, **kwargs):
        a = self.default_meta_extraction().items()
        b = self.extracted_data.get('meta', {}).items()
        c = self.meta.items()

        new_meta = dict(a + b + c)

        for key, value in kwargs.items():
            exists = new_meta.setdefault(key, value)

            if exists != value:
                new_meta[key] = flatten_list(value, new_meta[key])

        return new_meta

    @staticmethod
    def extract_meta_data(meta_lines):
        return yaml.load(meta_lines)

    @property
    def as_HTML(self):
        template = self.as_MARKDOWN
        return markdown.markdown(
            template,
            output_format = self.site.config.get('output_format', 'html'))

    @property
    def as_MARKDOWN(self):
        template = Template(self.extracted_data.get('content', ''))
        template = template.render(**self.metadata)
        return template


class Category(object):
    def __init__(self, raw):
        self.raw_category = raw

    @staticmethod
    def category_from_filename(f):
        pass

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
        c = asset.meta.get('categories', []) + path_categories

        # filter the categories so they're all lowercase
        c = map(lambda x: x.lower(), c)

        return c

