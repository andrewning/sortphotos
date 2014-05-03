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
import subprocess
import filecmp
import glob
from datetime import datetime, timedelta

import exifread




# -------- convenience methods -------------

def parse_date_exif(date_string):
    """
    extract date info from EXIF data
    YYYY:MM:DD HH:MM:SS
    """

    date_array, time_array = str(date_string).split()
    date_entries = date_array.split(':')
    time_entries = time_array.split(':')
    year = int(date_entries[0])
    month = int(date_entries[1])
    day = int(date_entries[2])

    hour = int(time_entries[0])
    minute = int(time_entries[1])
    second = int(time_entries[2])

    return datetime(year, month, day, hour, minute, second)


def parse_date_tstamp(fname):
    """extract date info from file timestamp"""

    # time of last modification
    if os.name == 'nt':  # windows allows direct access to creation date
        creation_time = os.path.getctime(fname)
    else:
        creation_time = get_creation_time(fname)

    return datetime.fromtimestamp(creation_time)


def year_month_day(date, day_begins):

    # check for early hour photos to be grouped with previous day
    if date.hour < day_begins:
        newdate = date - timedelta(hours=date.hour+1)  # push it to the day before for classificiation purposes
    else:
        newdate = date

    year = str(newdate.year)
    month = '{0:02d}'.format(newdate.month)
    month += '-' + months[month]
    day = '{0:02d}'.format(newdate.day)
    week = '{0:02d}'.format(int(date.strftime("%W")) + 1) # +1 sinc strftime("%W") starts at 0

    return year, month, day, week


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

SortType = enum('Year', 'YearMonth', 'YearMonthDay', 'YearWeek')

# ----------------------------------





# --------- main script -----------------

def sortPhotos(src_dir, dest_dir, extensions, sort_type, move_files, removeDuplicates,
               ignore_exif, day_begins):


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

        if ignore_exif:
            date = parse_date_tstamp(src_file)

        else:
            # open file
            f = open(src_file, 'rb')

            tags = exifread.process_file(f, details=False)

            f.close()

            # look for date in EXIF data
            if 'EXIF DateTimeDigitized' in tags and valid_date(tags['EXIF DateTimeDigitized']):
                date = parse_date_exif(tags['EXIF DateTimeDigitized'])

            elif 'EXIF DateTimeOriginal' in tags and valid_date(tags['EXIF DateTimeOriginal']):
                date = parse_date_exif(tags['EXIF DateTimeOriginal'])

            elif 'Image DateTime' in tags and valid_date(tags['Image DateTime']):
                date = parse_date_exif(tags['Image DateTime'])

            else:  # use file time stamp if no valid EXIF data
                date = parse_date_tstamp(src_file)


        year, month, day, week = year_month_day(date, day_begins)

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

        # create week directory if necessary
        if sort_type == SortType.YearWeek:
            dest_file = os.path.join(dest_file, week)
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
    parser.add_argument('-s', '--sort', type=str, choices=['y', 'm', 'd', 'w'], default='m',
                        help='choose destination folder structure\n\ty: sort by year\n\tm: sort by year then month\n\td: sort by year then month then day\n\tw: sort by year then week')
    parser.add_argument('--keep-duplicates', action='store_true',
                        help='If file is a duplicate keep it anyway (after renmaing).')
    parser.add_argument('--extensions', type=str, nargs='+',
                        default=['jpg', 'jpeg', 'tiff', 'arw', 'avi', 'mov', 'mp4', 'mts'],
                        help='file types to sort')
    parser.add_argument('--ignore-exif', action='store_true',
                        help='always use file time stamp even if EXIF data exists')
    parser.add_argument('--day-begins', type=int, default=0, help='hour of day that new day begins (0-23), \
                        defaults to 0 which corresponds to midnight.  Useful for gropuing pictures with \
                        previous day.')


    # parse command line arguments
    args = parser.parse_args()

    if args.sort == 'y':
        sort_type = SortType.Year
    elif args.sort == 'm':
        sort_type = SortType.YearMonth
    elif args.sort == 'd':
        sort_type = SortType.YearMonthDay
    elif args.sort == 'w':
        sort_type = SortType.YearWeek

    sortPhotos(args.src_dir, args.dest_dir, args.extensions, sort_type,
              args.move, not args.keep_duplicates, args.ignore_exif, args.day_begins)



