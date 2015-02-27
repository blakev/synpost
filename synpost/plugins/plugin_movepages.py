__author__ = 'Blake'

import os
import shutil

from synpost.plugins.core import PluginCore

class MovePagesPlugin(PluginCore):
    action = 'build'
    priority = 100

    @staticmethod
    def execute(Action):
        page_files_in_root = Action.config.get('page_files_in_root', True)
        assets_as_pages = Action.config.get('assets_as_pages', True)

        if not page_files_in_root:
            return True

        pages_directory = os.path.join(Action.config['project_destination'], 'pages')

        files_to_move = set()
        theme_assets = set()

        # Action.site.theme.REQUIRED_PIECES + "additional_page_assets" in config
        conf_pieces = [os.path.split(x)[1] for x in Action.config.get('additional_page_assets', [])]
        conf_pieces = ['.'.join(os.path.split(x)[1].split('.')[:-1]) for x in conf_pieces]
        req_pieces = list(Action.site.theme.REQUIRED_PIECES)
        req_pieces.extend(conf_pieces)

        for f in os.listdir(pages_directory):
            full_file = os.path.join(pages_directory, f)

            if os.path.isfile(full_file):
                if page_files_in_root:
                    files_to_move.add(full_file)

                if not assets_as_pages:
                    valiname = '.'.join(os.path.split(full_file)[1].split('.')[:-1])

                    if valiname in req_pieces:
                        theme_assets.add(full_file)

        # take the theme_assets out of the "all files we're moving" if we don't want them
        # to overwrite files in the actual theme directory
        new_files_full = list(files_to_move.difference(theme_assets))
        new_files_name = [os.path.split(n)[1] for n in new_files_full]

        pages_path = os.path.join(Action.dest_folder, 'pages')
        available_pages = filter(os.path.isfile, [os.path.join(pages_path, o) for o in os.listdir(pages_path)])

        for fullpath, name in zip(new_files_full, new_files_name):
            if fullpath in available_pages:
                shutil.move(fullpath, os.path.join(Action.dest_folder, name))

        return True

