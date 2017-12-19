
# Description

SortPhotos is a Python script that organizes photos into folders by date and/or time (year, year/month, year/month/day, or other custom formats).  If you're like me then your growing collection of files are contained in a bunch of folders, some with a date like "Sep 2010", and others which names like "Camping Trip".  SortPhotos takes this collection of folders and files and reorganizes them into a hierarchy of folders by almost any custom date/time format (by default it is by year then month).  It will work with any file, but works best with image and video files that contain EXIF or other metadata formats because that stays with the file even if the files are modified.  The script is also useful for transferring files from your camera into your collection of nicely organized photos.

![Example](example.png)

# Download
Find the lastest releases here:
https://github.com/TeaWithLucas/Sort-Photos/releases

# Usage

SortPhotos is intended to be used primarily from the command line.  To see all the options, invoke help

    python sortphotos.py -h

The simplest usage is to specify a source directory (the directory where your mess of files is currently located) and a destination directory (where you want the files and directories to go).  By default the source directory it is not searched recursively but that can changed with a flag as discussed below.

    python sortphotos.py /Users/Me/MessyDirectory /Users/Me/Pictures
    

Full documentation or futher information here:
https://github.com/TeaWithLucas/Sort-Photos/wiki
