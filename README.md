# SortPhotos

SortPhotos is a Python script that organizes photos into folders by date and/or time (year, year/month, year/month/day, or other custom formats).  If you're like me then your growing collection of files are contained in a bunch of folders, some with a date like "Sep 2010", and others which names like "Camping Trip".  SortPhotos takes this collection of folders and files and reorganizes them into a hierarchy of folders by almost any custom date/time format (by default it is by year then month).  It will work with any file, not just photos, but it works best with *.jpg, *.tiff, and *raw files because it can use EXIF data that stays with the file.  For other files (like *.mov or *.avi) SortPhotos will sort them using the creation date.  The script is also useful for transferring files from your camera into your collection of nicely organized photos.

![Example](example.png)

# Usage

SortPhotos is intended to be used primarily from the command line.  To see all the options, invoke help

    python sortphotos.py -h

The simplest usage is to specify a source directory (the directory where your mess of files is currently located---it will be searched recursively) and a destination directory (where you want the files and directories to go).

    python sortphotos.py /Users/Me/MessyDirectory /Users/Me/Pictures

## move rather than copy
There are several options that can be invoked.  For example the default behavior is to copy files from your source directory to your destination directory.  That is useful, for example, if you're copying files from your camera.  However, if you just want to organize existing files on your computer it's **much** faster to move the files rather than copy them (especially if videos are involved).  This is done with the ``-m`` or ``--move`` flag.

    python sortphotos.py -m /source /destination

## sort in directories
By default folders are sorted by year then month, with both the month number and name.  So for example if cool_picture.jpg was taken on June 1, 2010 the resulting directory hierarchy will look like: 2010 > 06-Jun > cool_picture.jpg.  However, you can customize the sorting style almost anyway you want.  The script takes an optional argument ``-s`` or ``--sort``, which accepts a format string using the conventions described [here](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior).  To separate by subdirectory, just use a forward slash (even if you are on Windows).    So for example, the default sorting behavior (2010/06-Jun) is equivalent to:

    python sortphotos.py --sort %Y/%m-%b

 Or you could sort just by month, but with the month full name (June):

    python sortphotos.py --sort %B

Or you can sort by year without century, then week number, then an abbreviated day of the week (10/23/Sun)

    python sortphotos.py --sort %y/%U/%a

The possibilities go on and on.

## duplicate removal
SortPhotos will *always* check to make sure something with the same file name doesn't already exist where it's trying to write, so that you don't unintentionally overwrite a file. It this occurs it will append a number on the end of the file.  So for example if photo.jpg was taken on June 1, 2010 but 2010 > June > photo.jpg already exists then the new file will be copied as photo_1.jpg and so on.  SortPhotos will go one step further and if it finds a file of the same name, it will then run a file compare to see if the files are actually the same.  If they are *exactly* the same, it will just skip the copy (or move) operation.  This will prevent you from having duplicate files.  However you have the option of turning this off (not the name comparison, that will always happen, just the weeding out of duplicates).  This option would be useful, for example, if you are copying over a bunch of new photos that you are sure don't already exist in your organized collection of photos.  It's a little faster to skip duplicate detection.   Invoke the option ``--keep-duplicates`` in order to skip duplicate detection.

    python sortphotos.py --keep-duplicates /source /destination

## choose which file types to search for
You can restrict what types of files SortPhotos looks for in your source directory.  By default it only looks for the most common photo and video containers ('jpg', 'jpeg', 'tiff', 'arw', 'avi', 'mov', 'mp4', 'mts').  You can change this behavior through the ``extensions`` argument.  Note that it is not case sensitive so if you specify 'jpg' as an extension it will search for both jpg and JPG files or even jPg files.  For example say you want to copy and sort only the *.gif and *.avi files you would call

    python sortphotos.py /source /destination --extensions gif avi

If you only want to sort the files that (potentially) have EXIF data then

    python sortphotos.py /source /destination --extensions jpg tiff

You may want to use this for files that aren't photos or videos at all

    python sortphotos.py /source /destination --extensions docx xlsx pptx

To sort every possible file type

    python sortphotos.py /source /destination --extensions *

However, this option will copy even hidden files like .DS_Store.

## ignore EXIF
If you don't want to use EXIF data at all (even if it exists) and just use time stamps you can add the ``--ignore-exif`` flag.

## change time of day when the day "begins"
If you are taking photos for an event that goes past midnight, you might want the early morning photos to be grouped with those from the previous day.  By default the new day begins at midnight, but if you wanted any photos taken before 4AM to be grouped with the previous day you can use  
``--day-begins 4``  
The argument to the flag should be an integer between 0-23 corresponding to the hours of the day starting at midnight.

## retrieve date from filename before system creation date
If you want to get date from the filename (like IMG_22032013.jpg) you can use --filename-parse with one of the following flags

* L or l for little median (DDMMYYYY)
* M or m for middle median (MMDDYYYY)
* B or b for big median (YYYYMMDD)
* T or t for time in the day (HHMMSS)
* A or a for ask anytime several dates are found in the filename (like 12042014 can be 12th April or 4th December)

## verbose mode
If you want to output informations, use the -v --verbose 

## simulation mode
If you want to test your combinaison of flags before moving/copying your files you can add --simulation to output every informations that should happen without actually do them

# Automation

*Note while sortphotos.py was written in a cross-platform way, the following instructions for automation are specific to OS X.  For other operating systems there are of course ways to schedule tasks or submit cron jobs, but I will leave that as an exercise to the reader.*

An an optional setup, I like to automate the process of moving my photos.  This can be accomplished simply on OS X using Launch Agents.  First edit the supplied plist file ``com.andrewning.sortphotos.plist`` in any text editor.  On line 10 enter the **full path** of where ``sortphotos.py`` is stored.  On line 12 enter the full path of your source directory (I use the [PhotoSync iOS App](http://www.photosync-app.com) to transfer photos from my phone to my computer so they all end up in folder called PhotoSync, but this can be any folder you like).  One line 13 enter the full path of the destination top level directory (e.g., ``/Users/Me/Pictures``).  Finally, on line 16 you can change how often the script will run (in seconds).  I have it set to run once a day, but you can set it to whatever you like.

Now move the plist file to ``~/Library/LaunchAgents/``.  Switch to that directory and load it

    $ launchctl load com.andrewning.sortphotos.plist

That's it.  It will now run once a day automatically (or to whatever internal you picked).  Of course if there are no pictures in the source folder the script does nothing and will check again at the next interval.  There are ways to use folder listeners instead of a time-based execution, but this script is so lightweight the added complexity is unwarranted.  If you want to make sure your service is scheduled, execute

    $ launchctl list | grep sortphotos

and you should see the Agent listed (I grep the results because you will typically have many services running).  If you want to stop the script from running anymore just unload it.

    $ launchctl unload com.andrewning.sortphotos.plist

# Acknowledgments

SortPhotos grabs EXIF data from the photos using [exif-py](https://github.com/ianare/exif-py).

# License

Copyright (c) 2013, S. Andrew Ning.  All rights reserved.

All code is licensed under [The MIT License](http://opensource.org/licenses/mit-license.php).
