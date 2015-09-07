import os

WATCH_DIR   = "~/Documents/incoming_photos"
SORTED_DIR  = "~/Documents/sorted_photos"
FILTER_SORT = "~/Documents/sortphotos/src/sort_filter.py"

filter_sort_cmd = 'python '+FILTER_SORT+' "${event}" '+SORTED_DIR+' '+WATCH_DIR
fswatch_cmd     = 'fswatch -0 '+WATCH_DIR+' | while read -d "" event ; do '+filter_sort_cmd+' ; done ;'

os.system(fswatch_cmd)
