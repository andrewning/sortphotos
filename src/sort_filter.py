import os
import sys
import fnmatch
import errno

FILTERS = ["*.db",".*"]
REMOVE_FILTERED_FILES = True
SORTPHOTOS  = "~/Documents/sortphotos/src/sortphotos.py"

event = sys.argv[1]
sorted_dir = sys.argv[2]
watched_dir = sys.argv[3]

print "sorted_dir:",sorted_dir
print "event:",event

def do_exit(event):
	directory = os.path.split(event)[0]
	if os.path.normcase(os.path.normpath(directory)) != os.path.normcase(os.path.normpath(watched_dir)):
		try:
		    os.rmdir(directory)
		except OSError as ex:
		    if ex.errno == errno.ENOTEMPTY:
		        pass #directory is not empty, we don't remove it
	sys.exit(0)

if os.path.isdir(event):
	print "event is directory: ignoring"
	do_exit(event)

if not os.path.isfile(event):
	print "File has ever been processed."
	do_exit(event)

for _filter in FILTERS:
	if fnmatch.fnmatch(os.path.split(event)[-1], _filter):
		if REMOVE_FILTERED_FILES:
			print "event match filter [%s]: deleting."%(_filter)
			os.remove(event)
		else:
			print "event match filter [%s]: ignoring."%(_filter)
		do_exit(event)

print "Got valid event:"+event+" sorting..."

sortphotos_cmd  = 'python '+SORTPHOTOS+' --sort %Y/%m-%B --rename %y%m%d_%H%M_%S "'+event+'" '+sorted_dir
print "Applying command:"+sortphotos_cmd
os.system(sortphotos_cmd)
do_exit(event)