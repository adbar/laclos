#!/usr/bin/python3

###	This script is part of LACLOS (https://github.com/adbar/laclos).
###	Copyright (C) Adrien Barbaresi, 2013.
###	This is free software, licensed under the GNU Lesser General Public License (https://www.gnu.org/licenses/lgpl.html)


# purpose: filter subtitles based on language check results
# Python3 compatible

import argparse

# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--summary', dest='summary', help='summary of language statistics', required=True)
parser.add_argument('-o', '--output', dest='output', help='name of output file')
args = parser.parse_args()


badones = list()

with open(args.summary, 'r') as summaryfh:
    # skip first line
    next(summaryfh)
    for line in summaryfh:
        columns = line.split('\t')
        if float(columns[1]) > 50 or float(columns[2]) < 20 : # or columns[3] is not 'de'
            badones.append(int(columns[0]))

with open(args.output, 'w') as badonesfh:
    for item in badones.sort():
        badonesfh.write(str(item) + '\n')
