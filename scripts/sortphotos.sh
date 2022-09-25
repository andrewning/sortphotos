#!/usr/bin/env bash

(cd sortphotos/src ; python sortphotos.py -r --sort %Y-%m-%b --rename ofp-%Y-%m-%d-%H%M ./ouellet-family-pictures-IMPORT ./ouellet-family-pictures)
