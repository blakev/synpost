__author__ = 'Blake'

import os
import re
from collections import namedtuple

SiteFile = namedtuple('SiteFile', 'filename valiname filepath extension type')

# coerce all files from collect_files_from into objects with properties
def generic_collect(path, regex, ftype, nametuple = None):
    if nametuple is None:
        nametuple = SiteFile

    ret = []

    for item in collect_files_from(path, regex):
        name = item.split(os.path.sep)[-1]  # filename
        ext = os.path.splitext(item)[1]     # file extension

        # validation name, is the filename without extension
        valiname = '.'.join(name.split('.')[:-1])
        ret.append(nametuple(name, valiname, item, ext, ftype))

    return ret


# grab all the files matching with_filter from dest down...
def collect_files_from(dest, with_filter = None):
    if with_filter is None:
        with_filter = re.compile(r'.*', re.I)

    for root, folders, files in os.walk(dest):
        files = filter(lambda x: with_filter.match(x), files)

        for f in files:
            yield os.path.join(root, f)


# creates a folder structure from a given
# root folder_path and d, the dictionary (list, or str)
# containing all the folders to be created
# overwrite allows new folders to be created, if
# it's set to false then no new folders can be made
# and it will skip over them; this MAY throw an error
# later, but at least the contents of the folders it
# does reach will be cleared out
def create_folders_from_dict(root, d, overwrite = True):
    def make_dat_folder(somepath):
        if not os.path.exists(somepath) and overwrite:
            os.makedirs(somepath)
        for f in os.listdir(somepath):
            file_path = os.path.join(somepath, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except IOError, e:
                print 'Error deleting file %s: %s' % (file_path, e)

    make_dat_folder(root)

    if isinstance(d, dict):
        for folder, subfolders in d.items():
            make_dat_folder(os.path.join(root, folder))
            create_folders_from_dict(os.path.join(root, folder), subfolders, overwrite)

    elif isinstance(d, list):
        for folder in d:
            if isinstance(folder, str):
                make_dat_folder(os.path.join(root, folder))
            else:
                create_folders_from_dict(root, folder, overwrite)

    elif isinstance(d, str):
        make_dat_folder(os.path.join(root, d))

























