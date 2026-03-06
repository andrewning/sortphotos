# SortPhotos

SortPhotos is a Python CLI tool that organizes photos and videos into folders by date and/or time using EXIF and other metadata. It takes a messy collection of files and reorganizes them into a customizable hierarchy of date-based folders (by default, year then month). It works with any file, but works best with image and video files that contain EXIF or other metadata. The tool is also useful for transferring files from your camera into a nicely organized photo collection.

![Example](example.png)

## Requirements

- **Python 3.9+**
- **Perl** (required by the bundled [ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/))

## Install

```bash
pip install .
```

For development (includes pytest):

```bash
pip install -e ".[dev]"
```

## Usage

To see all options:

```bash
sortphotos -h
```

The simplest usage is to specify a source directory and a destination directory:

```bash
sortphotos /Users/Me/MessyDirectory /Users/Me/Pictures
```

### Copy rather than move

The default behavior is to move files. Moving is **much** faster than copying, especially with videos. To copy instead:

```bash
sortphotos -c /source /destination
```

### Search recursively

By default, only the top level of the source directory is searched. To search recursively:

```bash
sortphotos -r /source /destination
```

### Verbosity control

By default a progress bar and summary are shown. Use ``-v`` or ``--verbose`` for detailed per-file processing information. Use ``-s``/``--silent`` or ``--quiet`` to suppress all output except errors.

```bash
sortphotos -v /source /destination      # detailed output
sortphotos --quiet /source /destination  # errors only
```

### Test mode (dry run)

Simulate what will happen without moving or copying any files. A summary is printed at the end:

```bash
sortphotos -t /source /destination
```

### Custom directory sorting

By default folders are sorted by year then month (e.g., `2010/06-Jun/cool_picture.jpg`). Customize with `--sort` using [strftime format codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior). Use forward slashes to create subdirectories (even on Windows).

```bash
sortphotos --sort %Y/%m-%b /source /destination  # default: 2010/06-Jun
sortphotos --sort %B /source /destination         # by month name: June
sortphotos --sort %y/%W/%a /source /destination   # year/week/day: 10/23/Sun
```

### Automatic file renaming

Rename files based on their date using the same strftime format codes:

```bash
sortphotos --rename %Y_%m%d_%H%M /source /destination
```

This creates files like `2003_1031_1544.jpg`. The original extension is preserved (lowercased). A unique number is appended in case of name collisions.

### Restrict metadata tags

SortPhotos searches all metadata for date information and uses the oldest date found. You can control which groups/tags are searched. All groups/tags are described in the [ExifTool Tag Names documentation](http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/).

```bash
# Ignore file timestamps (not persistent)
sortphotos --ignore-groups File /source /destination

# Ignore specific tags
sortphotos --ignore-tags File:FileModifyDate File:FileCreateDate /source /destination

# Only search specific groups
sortphotos --use-only-groups EXIF XMP IPTC /source /destination

# Only search specific tags
sortphotos --use-only-tags EXIF:CreateDate EXIF:DateTimeOriginal /source /destination
```

### Duplicate removal

SortPhotos always checks for filename collisions and appends a number to avoid overwriting (e.g., `photo_1.jpg`, `photo_2.jpg`). By default, it also detects identical files (same name and content) and skips them. To disable duplicate detection:

```bash
sortphotos --keep-duplicates /source /destination
```

### Exclude files by pattern

Exclude files from processing using glob patterns:

```bash
sortphotos --exclude "*.raw" "*.cr2" /source /destination
```

### Parallel file operations

Speed up large copy/move operations with multiple workers:

```bash
sortphotos -j 4 /source /destination
```

The default is `-j 1` (serial processing).

### Early morning photo grouping

Group photos taken in the early morning hours with the previous day. For example, to treat anything before 4 AM as the previous day:

```bash
sortphotos --day-begins 4 /source /destination
```

## Automation (macOS)

You can automate SortPhotos on macOS using Launch Agents. Edit the supplied plist file `com.andrewning.sortphotos.plist`:

1. Set the full path to `sortphotos` on line 10
2. Set your source directory on line 12
3. Set your destination directory on line 13
4. Optionally change the run interval on line 16 (default: 86400 seconds = once daily)

Then load it:

```bash
cp src/com.andrewning.sortphotos.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.andrewning.sortphotos.plist
```

To verify it's running: `launchctl list | grep sortphotos`

To stop: `launchctl unload ~/Library/LaunchAgents/com.andrewning.sortphotos.plist`

For other operating systems, use your platform's task scheduler (cron, Task Scheduler, etc.).

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## Acknowledgments

SortPhotos grabs EXIF data from photos/videos using the excellent [ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/) by Phil Harvey.

## License

Copyright (c) 2013, S. Andrew Ning. All rights reserved.

All code is licensed under [The MIT License](http://opensource.org/licenses/mit-license.php).
