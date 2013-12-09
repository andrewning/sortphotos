#!/usr/bin/env python
# encoding: utf-8
"""
sortphotos.py

Created on 3/2/2013
Copyright (c) S. Andrew Ning. All rights reserved.

"""

import os
import sys
import shutil
import fnmatch
import time
import subprocess
import filecmp

import exifread




# -------- convenience methods -------------

def parse_date_exif(date):
    """extract date info from EXIF data"""

    date = str(date).split()[0]
    entries = date.split(':')
    year = entries[0]
    month = entries[1]
    month += '-' + months[month]
    day = entries[2]

    return year, month, day


def parse_date_tstamp(fname):
    """extract date info from file timestamp"""

    # time of last modification
    if os.name == 'nt':  # windows allows direct access to creation date
        creation_time = os.path.getctime(fname)
    else:
        creation_time = get_creation_time(fname)

    date = time.gmtime(creation_time)
    year = str(date.tm_year)
    month = '{0:02d}'.format(date.tm_mon)
    month += '-' + months[month]
    day = '{0:02d}'.format(date.tm_mday)

    return year, month, day


def valid_date(date):
    """check if date is not zero time"""

    elts = str(date).split(':')
    if len(elts) > 0 and elts[0] > '0000':
        return True
    else:
        return False


# Courtesy of Alec Thomas (http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python)
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


# Modification of --> Miles (http://stackoverflow.com/questions/946967/get-file-creation-time-with-python-on-mac)
def get_creation_time(path):
    if sys.platform.startswith('linux'):
        flag = '-c %Y'
    else:  # OS X
        flag = '-f %B'

    p = subprocess.Popen(['stat', flag, path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise OSError(p.stderr.read().rstrip())
    else:
        return int(p.stdout.read())

# ---------------------------------------


# ---------- constants --------------

months = {'01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR', '05': 'MAY',
          '06': 'JUN', '07': 'JUL', '08': 'AUG', '09': 'SEP', '10': 'OCT',
          '11': 'NOV', '12': 'DEC'}

SortType = enum('Year', 'YearMonth', 'YearMonthDay')

# ----------------------------------





# --------- main script -----------------

def sortPhotos(src_dir, dest_dir, extensions, sort_type, move_files, removeDuplicates):


    # some error checking
    if not os.path.exists(src_dir):
        raise Exception('Source directory does not exist')
    if not os.path.exists(dest_dir):
        raise Exception('Destination directory does not exist')


    # find files that have the specified extensions
    matched_files = []

    # check if file system is case sensitive
    case_sensitive_os = True
    if os.path.normcase('A') == os.path.normcase('a'):
        case_sensitive_os = False

    # recurvsively search directory
    for root, dirnames, filenames in os.walk(src_dir):

        # search for all files that match the extension
        for ext in extensions:

            # grab both upper and lower case matches if necessary
            matches = fnmatch.filter(filenames, '*.' + ext.lower())
            if case_sensitive_os:
                matches += fnmatch.filter(filenames, '*.' + ext.upper())

            # add file root and save the matched file in list
            for match in matches:
                matched_files.append(os.path.join(root, match))


    # setup a progress bar
    num_files = len(matched_files)
    idx = 0


    for src_file in matched_files:

        # update progress bar
        numdots = int(20.0*(idx+1)/num_files)
        sys.stdout.write('\r')
        sys.stdout.write('[%-20s] %d of %d ' % ('='*numdots, idx+1, num_files))
        sys.stdout.flush()

        idx += 1

        # open file
        f = open(src_file, 'rb')

        # get extension for types that may have EXIF data
        root, ext = os.path.splitext(src_file)

        if ext.lower() in ['.jpg', '.jpeg', '.tiff']:

            tags = exifread.process_file(f, details=False)

            # look for date in EXIF data
            if 'EXIF DateTimeDigitized' in tags and valid_date(tags['EXIF DateTimeDigitized']):
                year, month, day = parse_date_exif(tags['EXIF DateTimeDigitized'])

            elif 'EXIF DateTimeOriginal' in tags and valid_date(tags['EXIF DateTimeOriginal']):
                year, month, day = parse_date_exif(tags['EXIF DateTimeOriginal'])

            elif 'Image DateTime' in tags and valid_date(tags['Image DateTime']):
                year, month, day = parse_date_exif(tags['Image DateTime'])

            else:  # use file time stamp
                year, month, day = parse_date_tstamp(src_file)


        # if no EXIF data use file timestamp
        else:
            year, month, day = parse_date_tstamp(src_file)



        # create year directory if necessary
        dest_file = os.path.join(dest_dir, year)
        if not os.path.exists(dest_file):
            os.makedirs(dest_file)

        # create month directory if necessary
        if sort_type in [SortType.YearMonth, SortType.YearMonthDay]:
            dest_file = os.path.join(dest_file, month)
            if not os.path.exists(dest_file):
                os.makedirs(dest_file)

        # create day directory if necessary
        if sort_type == SortType.YearMonthDay:
            dest_file = os.path.join(dest_file, day)
            if not os.path.exists(dest_file):
                os.makedirs(dest_file)

        # setup destination file
        dest_file = os.path.join(dest_file, os.path.basename(src_file))
        root, ext = os.path.splitext(dest_file)

        # check for collisions
        append = 1
        fileIsIdentical = False

        while True:

            if os.path.isfile(dest_file):  # check for existing name
                if removeDuplicates and filecmp.cmp(src_file, dest_file):  # check for identical files
                    fileIsIdentical = True
                    break

                else:  # name is same, but file is different
                    dest_file = root + '_' + str(append) + ext
                    append += 1

            else:
                break


        # finally move or copy the file
        if move_files:
            os.rename(src_file, dest_file)
        else:
            if fileIsIdentical:
                continue  # if file is same, we just ignore it (for copy option)
            else:
                shutil.copy2(src_file, dest_file)


    print



if __name__ == '__main__':

    import argparse

    # setup command line parsing
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Sort files (primarily photos) into folders by date\nusing EXIF data if possible and file creation date if not')
    parser.add_argument('src_dir', type=str, help='source directory (searched recursively)')
    parser.add_argument('dest_dir', type=str, help='destination directory')
    parser.add_argument('-m', '--move', action='store_true', help='move files instead of copy')
    parser.add_argument('-s', '--sort', type=str, choices=['y', 'm', 'd'], default='m',
                        help='choose destination folder structure\n\ty: sort by year\n\tm: sort by year then month\n\td: sort by year then month then day')
    parser.add_argument('--keep-duplicates', action='store_true',
                        help='If file is a duplicate keep it anyway (after renmaing).')
    parser.add_argument('--extensions', type=str, nargs='+',
                        default=['jpg', 'jpeg', 'tiff', 'avi', 'mov', 'mp4'],
                        help='file types to sort')


    # parse command line arguments
    args = parser.parse_args()

    if args.sort == 'y':
        sort_type = SortType.Year
    elif args.sort == 'm':
        sort_type = SortType.YearMonth
    elif args.sort == 'd':
        sort_type = SortType.YearMonthDay

    sortPhotos(args.src_dir, args.dest_dir, args.extensions, sort_type,
              args.move, not args.keep_duplicates)



