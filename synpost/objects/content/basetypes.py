__author__ = 'Blake'

import os
import re
import json
import time
import types
import mimetypes

import markdown
import yaml
from jinja2 import Template

from synpost.fn.conversions import pretty_size, convert_sysdate, \
    flatten_list, path_to_asset, clean_filename, merge_dicts

# bootstrap mimetypes table with MARKDOWN extension
mimetypes.types_map['.md'] = 'text/plain'

import synpost.objects

class Asset(object):
    theme_piece = 'generic.html'

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

        # root metadata
        self.plugin_metadata = {}
        self.metadata = merge_dicts(
            self.get_filesystem_metadata(),
            self.site.config.get('meta', {})
        )


    def get_filesystem_metadata(self):
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
            'generated': {
                'ctime': time.time(),
                'pretty': convert_sysdate(time.time(), self.site.config.get('date_format', None))
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

        return '/{type}/{date}/{name}.{extension}'.format(**cleans)

    @property
    def identifiers(self):
        return {
            'uuid': self.uuid,
            'shortname': self.shortname,
            'asset_path': path_to_asset(self.asset) + self.shortname,
            'href': self.href
        }


    @property
    def is_static(self):
        return True

    @property
    def uuid(self):
        the_year = convert_sysdate(self.metadata['created']['ctime'], '%Y')
        return '%s-%s' % (the_year, hex(int(self.metadata['created']['ctime']) & 0xffffff).split('x')[1])

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
    def name(self):
        return clean_filename(self.metadata.get('title', self.asset.valiname)).lower()

    @property
    def shortname(self):
        return '_'.join([c.lower() for c in self.name.split()])[:30].strip('_')

    @property
    def created(self):
        return self.metadata['created']['ctime']

    @property
    def updated(self):
        return self.metadata['last_edited']['ctime']

    def to_JSON(self):
        return json.dumps(self.name, default=lambda x: x.__dict__, sort_keys=True)

    def as_JSON(self):
        return self.__dict__

    def _mirror_contents(self):
        with open(self.path, 'r') as ins_file:
            lines = ins_file.readlines()
        return ''.join(lines)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<Asset.%s filename: "%s">' % (self.type.capitalize(), str(self.filename))


class TextContentAsset(Asset):
    metadata_regex = re.compile(r'(\$\$\n+(.*\n)*?\$\$)', re.I)
    whitespace_regex = re.compile(r'\w+', re.I + re.M)

    def __init__(self, asset_obj, site = None):
        super(TextContentAsset, self).__init__(asset_obj, site)

        with open(self.path, 'r') as ins_file:
            content_lines = ins_file.readlines()

        # get the content and the meta data blocks from the text file
        extracted = self.__extract(content_lines)

        # get the metadata blocks and the content blocks from the text asset
        self.extracted_data = {
            'meta': extracted[0], 'content': extracted[1]
        }

        # combine the inset config meta data into the root of the metaobject passed to jinja
        self.metadata = merge_dicts(self.metadata, self.extracted_data.get('meta', {}))

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

    @staticmethod
    def extract_meta_data(meta_lines):
        return yaml.load(meta_lines)

    @property
    def is_static(self):
        return False

    @property
    def jinja_obj(self):
        x = {
            'plugins': self.plugin_metadata,
            'extra': {
                'href': self.href,
                'page_id': self.identifiers['uuid'],
                'short_name': self.shortname,
                'name': self.name,
                'extension': self.extension
            },
            'meta': self.metadata,
            'site': {
                'articles': [(x.metadata.get('title', x.asset.valiname), x.href) for x in self.site.ordered_articles],
                'article_index': None if not self.type == 'articles' else self.site.article_index(self),
                'pages': self.site.all_pages
            }
        }
        return x

    @property
    def finalized_html(self):
        return self.as_HTML

    @property
    def as_HTML(self):
        template = self.as_MARKDOWN
        return markdown.markdown(
            template,
            output_format = self.site.config.get('output_format', 'html'))

    @property
    def as_MARKDOWN(self):
        template = Template(self.extracted_data.get('content', ''))
        template = template.render(**self.jinja_obj)
        return template
