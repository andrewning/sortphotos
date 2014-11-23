#!/usr/bin/env python
# encoding: utf-8
"""
sortphotos.py

Created on 3/2/2013
Copyright (c) S. Andrew Ning. All rights reserved.

"""

import subprocess
import os

exiftool_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Image-ExifTool', 'exiftool')


#  this class is based on code from Sven Marnach (http://stackoverflow.com/questions/10075115/call-exiftool-from-a-python-script)
class ExifTool(object):

    sentinel = "{ready}\n"

    def __init__(self, executable=exiftool_location):
        self.executable = executable

    def __enter__(self):
        self.process = subprocess.Popen(
            [self.executable, "-stay_open", "True",  "-@", "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.process.stdin.write("-stay_open\nFalse\n")
        self.process.stdin.flush()

    def execute(self, *args):
        args = args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args))
        self.process.stdin.flush()

        for line in iter(self.process.stdout.readline, b''):
            if line.endswith(self.sentinel):
                break
            print(line.rstrip())

    # def get_metadata(self, *filenames):
    #     return json.loads(self.execute('-j', '-n', '-a', '-r', '-time:all', *filenames))





def sortPhotos(src_dir, dest_dir, sort_key, rename_key, sort_tags, recursive=True,
        copy=False, show_progress=True, test=False):
    """
    This function is a convenience wrapper around ExifTool based on common usage scenarios for sortphotos.py

    Parameters
    ---------------
    src_dir : str
        directory containing files you want to process
    dest_dir : str
        directory where you want to move/copy the files to
    sort_key : str
        date format code for how you want your photos sorted (http://www.sno.phy.queensu.ca/~phil/exiftool/filename.html#codes)
    rename_key : str
        date format code for how you want your files renamed (http://www.sno.phy.queensu.ca/~phil/exiftool/filename.html#codes)
    sort_tags : list(str)
        a list of tags that are used to find date/time information.  tags should be provided in order of priority.
        (http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/index.html)
    recursive : bool
        True if you want src_dir to be searched recursively for files (False to search only in top-level of src_dir)
    copy : bool
        True if you want files to be copied over from src_dir to dest_dir rather than moved
    show_progress : bool
        True if you want to see progress of file processing
    test : bool
        True if you just want to simulate how the files will be moved without actually doing any moving/copying

    """

    # format directory/file structure
    location = dest_dir
    if len(sort_key) > 0:
        location += '/' + sort_key
    location += '/' + rename_key

    # set flags
    flags = ['-a']  # process duplicate tags
    fileflag = '-filename'

    if copy:
        flags += ['-o', '.']
    if recursive:
        flags += ['-r']
    if show_progress and not test:
        flags += ['-progress']
    if test:
        fileflag = '-testname'
        print '--- Preview ---'
        print

    # setup tags to sort by
    rename = []
    for tag in sort_tags:
        rename = [fileflag + '<{0}'.format(tag)] + rename

    # run exiftool
    args = flags + ['-d', location] + rename + [src_dir]

    with ExifTool() as e:
            e.execute(*args)




if __name__ == '__main__':

    import argparse

    # setup command line parsing
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Sort files (primarily photos and videos) into folders by date\nusing EXIF data if possible and file creation date if not')
    parser.add_argument('src_dir', type=str, help='source directory')
    parser.add_argument('dest_dir', type=str, help='destination directory')
    parser.add_argument('-c', '--copy', action='store_true', help='copy files instead of move')
    parser.add_argument('-r', '--recursive', action='store_true', help='search src_dir recursively')
    parser.add_argument('-s', '--silent', action='store_true', help='don\'t display progress.  just statistics at end')
    parser.add_argument('-t', '--test', action='store_true', help='run a test.  files will not be moved/copied\ninstead you will just a list of would happen')
    parser.add_argument('--sort', type=str, default='%Y/%m-%b',
                        help="choose destination folder structure using datetime format \n\
    http://www.sno.phy.queensu.ca/~phil/exiftool/filename.html#codes. \n\
    Use forward slashes / to indicate subdirectory(ies) (independent of your OS convention). \n\
    The default is '%%Y/%%m-%%b', which separates by year then month \n\
    with both the month number and name (e.g., 2012/12-Feb).")
    parser.add_argument('--rename', type=str, default='%%f%%-c.%%e',
                        help="rename file using format codes \n\
    http://www.sno.phy.queensu.ca/~phil/exiftool/filename.html#codes. \n\
    The default is %%%%f%%%%-c.%%%%e', which is the original filename \n\
    + a unique digit if necessary in case of name collisiions + original extension \n\
    (e.g., myphoto.jpg or myphoto1.jpg).")
    parser.add_argument('--tags', type=str, nargs='+',
                    default=['CreationDate', 'DateTimeOriginal', 'DateTimeCreated', 'CreateDate', 'DateCreated', 'FileCreateDate', 'FileModifyDate'],
                    help='a list of tags (usually EXIF tags) that will be searched for to sort files.\n\
    tags should be provided in order of priority.\n\
    default is [\'CreationDate\', \'DateTimeOriginal\', \'DateTimeCreated\', \'CreateDate\', \n\
    \'DateCreated\', \'FileCreateDate\', \'FileModifyDate\']\n\
    list of tags here: http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/index.html')

    # parse command line arguments
    args = parser.parse_args()

    sortPhotos(args.src_dir, args.dest_dir, args.sort, args.rename, args.tags,
        args.recursive, args.copy, not args.silent, args.test)





