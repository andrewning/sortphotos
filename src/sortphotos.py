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
import re
from datetime import datetime, timedelta, date

import exifread




# -------- convenience methods -------------

bigMedian = re.compile('\D(?P<year>19\d{2}|20\d{2})[.\/ \-]?(?:(?P<month>0[1-9]|1[0-2])[.\/ \-]?(?P<day>\d{2}))\D') #Big Endian
middleMedian = re.compile('\D(?P<month>0[1-9]|1[0-2])[.\/ \-]?(?P<day>\d{2})[.\/ \-]?(?P<year>19\d{2}|20\d{2})\D')  #Middle Endian
littleMedian = re.compile('\D(?P<day>\d{2})[.\/ \-]?(?P<month>0[1-9]|1[0-2])[.\/ \-]?(?P<year>19\d{2}|20\d{2})\D') #Low Endian
time =  re.compile('\D(?P<hours>[0-1]\d|2[0-3])(?P<minutes>[0-5]\d)(?P<seconds>[0-5]\d)\D') #HHMMSS

def parse_date_exif(date_string):
    """
    extract date info from EXIF data
    YYYY:MM:DD HH:MM:SS
    """

    elements = str(date_string).strip().split()

    date_entries = elements[0].split(':')
    year = int(date_entries[0])
    month = int(date_entries[1])
    day = int(date_entries[2])

    if len(elements) > 1:
        time_entries = elements[1].split(':')
        hour = int(time_entries[0])
        minute = int(time_entries[1])
        second = int(time_entries[2])

    else:
        hour = 12  # defaulting to noon if no time data provided
        minute = 0
        second = 0

    return datetime(year, month, day, hour, minute, second)

def parse_filename_tstamp(flags,fname):
    #remove the path to get the basename
    fname = os.path.basename(fname)
    littleDate = None
    middleDate = None
    bigDate = None

    hours = None
    minutes = None
    seconds = None

    """extract time from filename"""
    if 't' in flags or 'T' in flags:
        r = time.search(fname)
        if r:
            hours = int(r.group('hours'))
            minutes = int(r.group('minutes'))
            seconds = int(r.group('seconds'))            

    """extract date from filaname"""
    if 'l' in flags or 'L' in flags:
        r = littleMedian.search(fname)
        if r:
          littleDate = datetime(int(r.group('year')),int(r.group('month')),int(r.group('day')))          
          if hours is not None:
              littleDate = littleDate.replace(hour=hours,minute=minutes,second=seconds)

    if 'm' in flags or 'M' in flags:
        r = middleMedian.search(fname)
        if r:
          middleDate = datetime(int(r.group('year')),int(r.group('month')),int(r.group('day')))          
          if hours is not None:
              middleDate = middleDate.replace(hour=hours,minute=minutes,second=seconds)

    if 'b' in flags or 'B' in flags:
        r = bigMedian.search(fname)
        if r:
          bigDate = datetime(int(r.group('year')),int(r.group('month')),int(r.group('day')))          
          if hours is not None:
              bigDate = bigDate.replace(hour=hours,minute=minutes,second=seconds)

    if 'a' in flags or 'A' in flags:
        inc = 0
        arrayDate = []
        if littleDate is not None:
            arrayDate.append(littleDate)
        if middleDate is not None:
            arrayDate.append(middleDate)
        if bigDate is not None:
            arrayDate.append(bigDate)

        if len(arrayDate) == 1:
            return arrayDate[0]
        if len(arrayDate) == 0:
            return False

        sys.stdout.write("\r\nfile: "+fname+"\r\n")
        if littleDate is not None:
            inc = inc + 1
            sys.stdout.write(str(inc)+")Little Median: "+littleDate.strftime("%a, %d %b %Y %H:%M:%S")+"\r\n")
        if middleDate is not None:
            inc = inc + 1
            sys.stdout.write(str(inc)+")Middle Median: "+middleDate.strftime("%a, %d %b %Y %H:%M:%S")+"\r\n")
        if bigDate is not None:
            inc = inc + 1
            sys.stdout.write(str(inc)+")Big Median: "+bigDate.strftime("%a, %d %b %Y %H:%M:%S")+"\r\n")

        while (True):
            r = raw_input("Please choose between choice (default 1): ")
            if not r :
                return arrayDate[0]
            
            if (r.isdigit() is False and r) or (int(r) < 1 or int(r) > inc):
                sys.stdout.write("\r\n"+r+" is not a valid choice\r\n")
                continue
            
            return arrayDate[int(r)-1]

    else:
        #choose the first one
        for i in range(0, len(flags)):
            if (i is 'l' or i is 'L') and (littleDate is not None):
                return littleDate
            if (i is 'm' or i is 'M') and (middleDate is not None):
                return middleDate
            if (i is 'b' or i is 'B') and (bigDate is not None):
                return bigDate

    return False

    
def parse_date_tstamp(fname):
    """extract date info from file timestamp"""

    # time of last modification
    if os.name == 'nt':  # windows allows direct access to creation date
        creation_time = os.path.getctime(fname)
    else:
        creation_time = get_creation_time(fname)

    return datetime.fromtimestamp(creation_time)


def check_for_early_morning_photos(date, day_begins):
    """check for early hour photos to be grouped with previous day"""

    if date.hour < day_begins:
        date = date - timedelta(hours=date.hour+1)  # push it to the day before for classificiation purposes

    return date


def valid_date(date):
    """check if date is not zero time and matches correct EXIF format: YYYY:MM:DD HH:MM:SS"""

    elements = str(date).strip().split()

    if (len(elements)) < 1:
        return False
    date_entries = elements[0].split(':')
    valid_date = len(date_entries) == 3 and date_entries[0] > '0000'
    valid_time = True

    if len(elements) > 1:
        valid_time = len(elements[1].split(':')) == 3

    return valid_date and valid_time


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


def log(str):
    if args.verbose:
        sys.stdout.write(str+"\r\n")

# ---------------------------------------




# --------- main script -----------------

def sortPhotos(src_dir, dest_dir, extensions, sort_format, move_files, removeDuplicates,
               ignore_exif, day_begins,filename_parse):


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

        log("\r\nParsing file "+src_file)
        
        if ignore_exif:
            if filename_parse is not None:
                date = parse_filename_tstamp(filename_parse,src_file)
                if date is False:
                    date = parse_date_tstamp(src_file)
                    log("date taken from file system timestamp: "+date.strftime("%A %d. %B %Y at %H:%M:%S"))
                else:
                    log("date taken from filename: "+date.strftime("%A %d. %B %Y at %H:%M:%S"))
            else:
                date = parse_date_tstamp(src_file)
                log("date taken from file system timestamp: "+date.strftime("%A %d. %B %Y at %H:%M:%S"))

        else:
            # open file
            f = open(src_file, 'rb')

            tags = exifread.process_file(f, details=False)

            f.close()
            # look for date in EXIF data
            if 'EXIF DateTimeOriginal' in tags and valid_date(tags['EXIF DateTimeOriginal']):
                date = parse_date_exif(tags['EXIF DateTimeOriginal'])
                log("date taken from EXIF DateTimeOriginal: "+date.strftime("%A %d. %B %Y at %H:%M:%S"))

            elif 'EXIF DateTimeDigitized' in tags and valid_date(tags['EXIF DateTimeDigitized']):
                date = parse_date_exif(tags['EXIF DateTimeDigitized'])
                log("date taken from EXIF DateTimeDigitized: "+date.strftime("%A %d. %B %Y at %H:%M:%S"))

            elif 'Image DateTime' in tags and valid_date(tags['Image DateTime']):
                date = parse_date_exif(tags['Image DateTime'])
                log("date taken from EXIF Image DateTime: "+date.strftime("%A %d. %B %Y at %H:%M:%S"))

            else:  # use file time stamp if no valid EXIF data
                if filename_parse is not None:
                    date = parse_filename_tstamp(filename_parse,src_file)

                    if date is False:
                        date = parse_date_tstamp(src_file)
                        log("date taken from file system timestamp: "+date.strftime("%A %d. %B %Y at %H:%M:%S"))
                    else:
                        log("date taken from filename: "+date.strftime("%A %d. %B %Y at %H:%M:%S"))
                else:
                    date = parse_date_tstamp(src_file)
                    log("date taken from file system timestamp: "+date.strftime("%A %d. %B %Y at %H:%M:%S"))
                


        # early morning photos can be grouped with previous day (depending on user setting)
        date = check_for_early_morning_photos(date, day_begins)

        # create folder structure
        dir_structure = date.strftime(sort_format)
        dirs = dir_structure.split('/')
        dest_file = dest_dir
        for thedir in dirs:
            dest_file = os.path.join(dest_file, thedir)
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
                log("file already exist")
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
            if fileIsIdentical:
                log("ignoring moving file")
                continue  # if file is same, we just ignore it 
            shutil.move(src_file, dest_file)
            log("file moved to "+dest_file)
        else:
            if fileIsIdentical:
                log("ignoring copying file")
                continue  # if file is same, we just ignore it
            else:
                shutil.copy2(src_file, dest_file)
                log("file copied to "+dest_file)


    print



if __name__ == '__main__':

    import argparse

    # setup command line parsing
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Sort files (primarily photos) into folders by date\nusing EXIF data if possible and file creation date if not')
    parser.add_argument('src_dir', type=str, help='source directory (searched recursively)')
    parser.add_argument('dest_dir', type=str, help='destination directory')
    parser.add_argument('-m', '--move', action='store_true', help='move files instead of copy')
    parser.add_argument('-s', '--sort', type=str, default='%Y/%m-%b',
                        help="choose destination folder structure using datetime format \n\
https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior. \n\
Use forward slashes / to indicate subdirectory(ies) (independent of your OS convention). \n\
The default is '%%Y/%%m-%%b', which separates by year then month \n\
with both the month number and name (e.g., 2012/12-Feb).")
    parser.add_argument('--keep-duplicates', action='store_true',
                        help='If file is a duplicate keep it anyway (after renmaing).')
    parser.add_argument('--extensions', type=str, nargs='+',
                        default=['jpg', 'jpeg', 'tiff', 'arw', 'avi', 'mov', 'mp4', 'mts'],
                        help='file types to sort')
    parser.add_argument('--filename-parse',type=str,default=None,help="check for date in filename before filesystem creation date,\n\
    L or l for little median (DDMMYYYY)\n\
    M or m for Middle median (MMDDYYYY)\n\
    B or b for Big median (YYYYMMDD)\n\
    T or t for time in the day (HHMMSS)\n\
    A or a for ask anytime a date is found (useful when you have multiple medians in your files)\n\
WARNING:you can use multiple flags but if you mix L M and B tags except somes bad results")
    parser.add_argument('-v','--verbose',default=False,action='store_true',help="verbose mode")
    parser.add_argument('--ignore-exif', action='store_true',
                        help='always use file time stamp even if EXIF data exists')
    parser.add_argument('--day-begins', type=int, default=0, help='hour of day that new day begins (0-23), \n\
defaults to 0 which corresponds to midnight.  Useful for grouping pictures with previous day.')


    # parse command line arguments
    args = parser.parse_args()

    sortPhotos(args.src_dir, args.dest_dir, args.extensions, args.sort,
              args.move, not args.keep_duplicates, args.ignore_exif, args.day_begins,args.filename_parse)



