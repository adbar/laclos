#!/usr/bin/python

###	This script is part of LACLOS (https://github.com/adbar/laclos).
###	Copyright (C) Adrien Barbaresi, 2013.

from __future__ import print_function
import re
import time
import sys

from os import listdir

# import atexit
import argparse

# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-n', dest='sets_number', help='number of sets to be created (200 each)', required=True)
args = parser.parse_args()

try: 
    sets_number = int(args.sets_number)
except ValueError:
    print ('number of sets is not an integer')
    sys.exit()


fileset = set()
for f in listdir('temp/'):
    match = re.search(r'^IMDBid_([0-9]+)$', f)
    if match:
        file_id = match.group(1)
        fileset.add(file_id)


print ('subs downloaded:', len(fileset))


todo = list()
id_dict = dict()
i = 0
listfile = open('metadata', 'r')
for line in listfile:
    columns = line.split('\t')
    if columns[0] not in fileset:
        todo.append(columns[2])
        id_dict[columns[2]] = columns[0]
    i += 1
listfile.close()

todo = list(set(todo))
print ('subs detected:', i)
print ('subs todo:', len(todo))


if sets_number != 0:
    #maxval = sets_number * 200
    i = 1
    while i <= sets_number:
        x = i * 200
        y = x - 200
        chunk = todo[y:x]
        filename = 'set_' + str(i)
        output = open(filename, 'w')
        for item in chunk:
            output.write(str(id_dict[item]) + '\t' + str(item) + '\n')
        output.close()
        i += 1




