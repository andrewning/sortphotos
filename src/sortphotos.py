#!/usr/bin/env python
# encoding: utf-8
"""
sortphotos.py

Created on 3/2/2013
Copyright (c) S. Andrew Ning. All rights reserved.

"""

from __future__ import print_function
from __future__ import with_statement
import subprocess
import os
import sys
import shutil
try:
    import json
except:
    import simplejson as json
import filecmp
from datetime import datetime, timedelta
import re
import locale

# Setting locale to the 'local' value
locale.setlocale(locale.LC_ALL, '')

exiftool_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Image-ExifTool', 'exiftool')


# -------- convenience methods -------------

def parse_date_exif(date_string):
    """
    extract date info from EXIF data
    YYYY:MM:DD HH:MM:SS
    or YYYY:MM:DD HH:MM:SS+HH:MM
    or YYYY:MM:DD HH:MM:SS-HH:MM
    or YYYY:MM:DD HH:MM:SSZ
    """

    # split into date and time
    elements = str(date_string).strip().split()  # ['YYYY:MM:DD', 'HH:MM:SS']

    if len(elements) < 1:
        return None

    # parse year, month, day
    date_entries = elements[0].split(':')  # ['YYYY', 'MM', 'DD']

    # check if three entries, nonzero data, and no decimal (which occurs for timestamps with only time but no date)
    if len(date_entries) == 3 and date_entries[0] > '0000' and '.' not in ''.join(date_entries):
        year = int(date_entries[0])
        month = int(date_entries[1])
        day = int(date_entries[2])
    else:
        return None

    # parse hour, min, second
    time_zone_adjust = False
    hour = 12  # defaulting to noon if no time data provided
    minute = 0
    second = 0

    if len(elements) > 1:
        time_entries = re.split('(\+|-|Z)', elements[1])  # ['HH:MM:SS', '+', 'HH:MM']
        time = time_entries[0].split(':')  # ['HH', 'MM', 'SS']

        if len(time) == 3:
            hour = int(time[0])
            minute = int(time[1])
            second = int(time[2].split('.')[0])
        elif len(time) == 2:
            hour = int(time[0])
            minute = int(time[1])

        # adjust for time-zone if needed
        if len(time_entries) > 2:
            time_zone = time_entries[2].split(':')  # ['HH', 'MM']

            if len(time_zone) == 2:
                time_zone_hour = int(time_zone[0])
                time_zone_min = int(time_zone[1])

                # check if + or -
                if time_entries[1] == '+':
                    time_zone_hour *= -1

                dateadd = timedelta(hours=time_zone_hour, minutes=time_zone_min)
                time_zone_adjust = True


    # form date object
    try:
        date = datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None  # errors in time format

    # try converting it (some "valid" dates are way before 1900 and cannot be parsed by strtime later)
    try:
        date.strftime('%Y/%m-%b')  # any format with year, month, day, would work here.
    except ValueError:
        return None  # errors in time format

    # adjust for time zone if necessary
    if time_zone_adjust:
        date += dateadd

    return date



def get_oldest_timestamp(data, additional_groups_to_ignore, additional_tags_to_ignore, print_all_tags=False):
    """data as dictionary from json.  Should contain only time stamps except SourceFile"""

    # save only the oldest date
    date_available = False
    oldest_date = datetime.now()
    oldest_keys = []

    # save src file
    src_file = data['SourceFile']

    # ssetup tags to ignore
    ignore_groups = ['ICC_Profile'] + additional_groups_to_ignore
    ignore_tags = ['SourceFile', 'XMP:HistoryWhen'] + additional_tags_to_ignore


    if print_all_tags:
        print('All relevant tags:')

    # run through all keys
    for key in data.keys():

        # check if this key needs to be ignored, or is in the set of tags that must be used
        if (key not in ignore_tags) and (key.split(':')[0] not in ignore_groups) and 'GPS' not in key:

            date = data[key]

            if print_all_tags:
                print(str(key) + ', ' + str(date))

            # (rare) check if multiple dates returned in a list, take the first one which is the oldest
            if isinstance(date, list):
                date = date[0]

            try:
                exifdate = parse_date_exif(date)  # check for poor-formed exif data, but allow continuation
            except Exception as e:
                exifdate = None

            if exifdate and exifdate < oldest_date:
                date_available = True
                oldest_date = exifdate
                oldest_keys = [key]

            elif exifdate and exifdate == oldest_date:
                oldest_keys.append(key)

    if not date_available:
        oldest_date = None

    if print_all_tags:
        print()

    return src_file, oldest_date, oldest_keys



def check_for_early_morning_photos(date, day_begins):
    """check for early hour photos to be grouped with previous day"""

    if date.hour < day_begins:
        print('moving this photo to the previous day for classification purposes (day_begins=' + str(day_begins) + ')')
        date = date - timedelta(hours=date.hour+1)  # push it to the day before for classificiation purposes

    return date


#  this class is based on code from Sven Marnach (http://stackoverflow.com/questions/10075115/call-exiftool-from-a-python-script)
class ExifTool(object):
    """used to run ExifTool from Python and keep it open"""

    sentinel = "{ready}"

    def __init__(self, executable=exiftool_location, verbose=False):
        self.executable = executable
        self.verbose = verbose

    def __enter__(self):
        self.process = subprocess.Popen(
            ['perl', self.executable, "-stay_open", "True",  "-@", "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.process.stdin.write(b'-stay_open\nFalse\n')
        self.process.stdin.flush()

    def execute(self, *args):
        args = args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args).encode('utf-8'))
        self.process.stdin.flush()
        output = ""
        fd = self.process.stdout.fileno()
        while not output.rstrip(' \t\n\r').endswith(self.sentinel):
            increment = os.read(fd, 4096)
            if self.verbose:
                sys.stdout.write(increment.decode('utf-8'))
            output += increment.decode('utf-8')
        return output.rstrip(' \t\n\r')[:-len(self.sentinel)]

    def get_metadata(self, *args):

        try:
            return json.loads(self.execute(*args))
        except ValueError:
            sys.stdout.write('No files to parse or invalid data\n')
            exit()


# ---------------------------------------



def sortPhotos(src_dir, dest_dir, sort_format, rename_format, recursive=False,
        copy_files=False, test=False, remove_duplicates=True, day_begins=0,
        additional_groups_to_ignore=['File'], additional_tags_to_ignore=[],
        use_only_groups=None, use_only_tags=None, verbose=True, keep_filename=False):
    """
    This function is a convenience wrapper around ExifTool based on common usage scenarios for sortphotos.py

    Parameters
    ---------------
    src_dir : str
        directory containing files you want to process
    dest_dir : str
        directory where you want to move/copy the files to
    sort_format : str
        date format code for how you want your photos sorted
        (https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior)
    rename_format : str
        date format code for how you want your files renamed
        (https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior)
        None to not rename file
    recursive : bool
        True if you want src_dir to be searched recursively for files (False to search only in top-level of src_dir)
    copy_files : bool
        True if you want files to be copied over from src_dir to dest_dir rather than moved
    test : bool
        True if you just want to simulate how the files will be moved without actually doing any moving/copying
    remove_duplicates : bool
        True to remove files that are exactly the same in name and a file hash
    keep_filename : bool
        True to append original filename in case of duplicates instead of increasing number
    day_begins : int
        what hour of the day you want the day to begin (only for classification purposes).  Defaults at 0 as midnight.
        Can be used to group early morning photos with the previous day.  must be a number between 0-23
    additional_groups_to_ignore : list(str)
        tag groups that will be ignored when searching for file data.  By default File is ignored
    additional_tags_to_ignore : list(str)
        specific tags that will be ignored when searching for file data.
    use_only_groups : list(str)
        a list of groups that will be exclusived searched across for date info
    use_only_tags : list(str)
        a list of tags that will be exclusived searched across for date info
    verbose : bool
        True if you want to see details of file processing

    """

    # some error checking
    if not os.path.exists(src_dir):
        raise Exception('Source directory does not exist')

    # setup arguments to exiftool
    args = ['-j', '-a', '-G']

    # setup tags to ignore
    if use_only_tags is not None:
        additional_groups_to_ignore = []
        additional_tags_to_ignore = []
        for t in use_only_tags:
            args += ['-' + t]

    elif use_only_groups is not None:
        additional_groups_to_ignore = []
        for g in use_only_groups:
            args += ['-' + g + ':Time:All']

    else:
        args += ['-time:all']


    if recursive:
        args += ['-r']

    args += [src_dir]


    # get all metadata
    with ExifTool(verbose=verbose) as e:
        print('Preprocessing with ExifTool.  May take a while for a large number of files.')
        sys.stdout.flush()
        metadata = e.get_metadata(*args)

    # setup output to screen
    num_files = len(metadata)
    print()

    if test:
        test_file_dict = {}

    # parse output extracting oldest relevant date
    for idx, data in enumerate(metadata):

        # extract timestamp date for photo
        src_file, date, keys = get_oldest_timestamp(data, additional_groups_to_ignore, additional_tags_to_ignore)

        # fixes further errors when using unicode characters like "\u20AC"
        src_file.encode('utf-8')

        if verbose:
        # write out which photo we are at
            ending = ']'
            if test:
                ending = '] (TEST - no files are being moved/copied)'
            print('[' + str(idx+1) + '/' + str(num_files) + ending)
            print('Source: ' + src_file)
        else:
            # progress bar
            numdots = int(20.0*(idx+1)/num_files)
            sys.stdout.write('\r')
            sys.stdout.write('[%-20s] %d of %d ' % ('='*numdots, idx+1, num_files))
            sys.stdout.flush()

        # check if no valid date found
        if not date:
            if verbose:
                print('No valid dates were found using the specified tags.  File will remain where it is.')
                print()
                # sys.stdout.flush()
            continue

        # ignore hidden files
        if os.path.basename(src_file).startswith('.'):
            print('hidden file.  will be skipped')
            print()
            continue

        if verbose:
            print('Date/Time: ' + str(date))
            print('Corresponding Tags: ' + ', '.join(keys))

        # early morning photos can be grouped with previous day (depending on user setting)
        date = check_for_early_morning_photos(date, day_begins)


        # create folder structure
        dir_structure = date.strftime(sort_format)
        dirs = dir_structure.split('/')
        dest_file = dest_dir
        for thedir in dirs:
            dest_file = os.path.join(dest_file, thedir)
            if not test and not os.path.exists(dest_file):
                os.makedirs(dest_file)

        # rename file if necessary
        filename = os.path.basename(src_file)

        if rename_format is not None and date is not None:
            _, ext = os.path.splitext(filename)
            filename = date.strftime(rename_format) + ext.lower()

        # setup destination file
        dest_file = os.path.join(dest_file, filename)
        root, ext = os.path.splitext(dest_file)

        if verbose:
            name = 'Destination '
            if copy_files:
                name += '(copy): '
            else:
                name += '(move): '
            print(name + dest_file)


        # check for collisions
        append = 1
        fileIsIdentical = False

        while True:

            if (not test and os.path.isfile(dest_file)) or (test and dest_file in test_file_dict.keys()):  # check for existing name
                if test:
                    dest_compare = test_file_dict[dest_file]
                else:
                    dest_compare = dest_file
                if remove_duplicates and filecmp.cmp(src_file, dest_compare):  # check for identical files
                    fileIsIdentical = True
                    if verbose:
                        print('Identical file already exists.  Duplicate will be ignored.\n')
                    break

                else:  # name is same, but file is different
                    if keep_filename:
                        orig_filename = os.path.splitext(os.path.basename(src_file))[0]
                        dest_file = root + '_' + orig_filename + '_' + str(append) + ext
                    else:
                        dest_file = root + '_' + str(append) + ext
                    append += 1
                    if verbose:
                        print('Same name already exists...renaming to: ' + dest_file)

            else:
                break


        # finally move or copy the file
        if test:
            test_file_dict[dest_file] = src_file

        else:

            if fileIsIdentical:
                continue  # ignore identical files
            else:
                if copy_files:
                    shutil.copy2(src_file, dest_file)
                else:
                    shutil.move(src_file, dest_file)



        if verbose:
            print()
            # sys.stdout.flush()


    if not verbose:
        print()


def main():
    import argparse

    # setup command line parsing
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Sort files (primarily photos and videos) into folders by date\nusing EXIF and other metadata')
    parser.add_argument('src_dir', type=str, help='source directory')
    parser.add_argument('dest_dir', type=str, help='destination directory')
    parser.add_argument('-r', '--recursive', action='store_true', help='search src_dir recursively')
    parser.add_argument('-c', '--copy', action='store_true', help='copy files instead of move')
    parser.add_argument('-s', '--silent', action='store_true', help='don\'t display parsing details.')
    parser.add_argument('-t', '--test', action='store_true', help='run a test.  files will not be moved/copied\ninstead you will just a list of would happen')
    parser.add_argument('--sort', type=str, default='%Y/%m-%b',
                        help="choose destination folder structure using datetime format \n\
    https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior. \n\
    Use forward slashes / to indicate subdirectory(ies) (independent of your OS convention). \n\
    The default is '%%Y/%%m-%%b', which separates by year then month \n\
    with both the month number and name (e.g., 2012/02-Feb).")
    parser.add_argument('--rename', type=str, default=None,
                        help="rename file using format codes \n\
    https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior. \n\
    default is None which just uses original filename")
    parser.add_argument('--keep-filename', action='store_true',
                        help='In case of duplicated output filenames an increasing number and the original file name will be appended',
                        default=False)
    parser.add_argument('--keep-duplicates', action='store_true',
                        help='If file is a duplicate keep it anyway (after renaming).')
    parser.add_argument('--day-begins', type=int, default=0, help='hour of day that new day begins (0-23), \n\
    defaults to 0 which corresponds to midnight.  Useful for grouping pictures with previous day.')
    parser.add_argument('--ignore-groups', type=str, nargs='+',
                    default=[],
                    help='a list of tag groups that will be ignored for date informations.\n\
    list of groups and tags here: http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/\n\
    by default the group \'File\' is ignored which contains file timestamp data')
    parser.add_argument('--ignore-tags', type=str, nargs='+',
                    default=[],
                    help='a list of tags that will be ignored for date informations.\n\
    list of groups and tags here: http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/\n\
    the full tag name needs to be included (e.g., EXIF:CreateDate)')
    parser.add_argument('--use-only-groups', type=str, nargs='+',
                    default=None,
                    help='specify a restricted set of groups to search for date information\n\
    e.g., EXIF')
    parser.add_argument('--use-only-tags', type=str, nargs='+',
                    default=None,
                    help='specify a restricted set of tags to search for date information\n\
    e.g., EXIF:CreateDate')

    # parse command line arguments
    args = parser.parse_args()

    sortPhotos(args.src_dir, args.dest_dir, args.sort, args.rename, args.recursive,
        args.copy, args.test, not args.keep_duplicates, args.day_begins,
        args.ignore_groups, args.ignore_tags, args.use_only_groups,
        args.use_only_tags, not args.silent, args.keep_filename)

if __name__ == '__main__':
    main()
