#!/usr/bin/python
# -*- coding: utf-8 -*-

###	This script is part of LACLOS (https://github.com/adbar/laclos).
###	Copyright (C) Adrien Barbaresi, 2014.
###	This is free software, licensed under the GNU Lesser General Public License (https://www.gnu.org/licenses/lgpl.html)


from __future__ import print_function

import re


hashes = set()
with open('dupresults_A', 'r') as f1:
    for line in f1:
        column = line.strip().split('\t')[1]
        hashes.add(column)

with open('dupresults_B', 'r') as f2:
    for line in f2:
        (filename, column) = line.strip().split('\t')
        if column in hashes:
            print ('rm', filename)
        else:
            hashes.add(column)
