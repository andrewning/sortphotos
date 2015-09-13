#!/usr/bin/env python
# encoding: utf-8
"""
file_wathcer.py

Created on 14/9/2015
Copyright (c) L. Dufréchou. All rights reserved.

"""

WATCH_DIR     = "~/Documents/incoming_photos"
SORTED_DIR    = "~/Documents/sorted_photos"
SORTPHOTOS    = "~/Documents/sortphotos/src/sortphotos.py"
FSWATCH       = "~/Documents/sortphotos/src/bin/fswatch"

USER_OPTIONS  = "--sort %Y/%m-%B --rename %y%m%d_%H%M_%S --set-locale fr_FR"

# Below this line there is no need to change anything
#-----------------------------------------------------------------------------------------------------------------------
MANDATORY_OPT = "-r --watch -s --ignore .* *.db --remove-ignored-files --remove-empty-dirs"

import os
sortphotos_cmd  = ' '.join(['python', SORTPHOTOS, MANDATORY_OPT, USER_OPTIONS, WATCH_DIR, SORTED_DIR])
fswatch_cmd     = FSWATCH+' '+WATCH_DIR+' | ' + sortphotos_cmd
os.system(fswatch_cmd)
