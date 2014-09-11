#!/usr/bin/python

###	This script is part of LACLOS (https://github.com/adbar/laclos).
###	Copyright (C) Adrien Barbaresi, 2013.
###	This is free software, licensed under the GNU Lesser General Public License (https://www.gnu.org/licenses/lgpl.html)


from __future__ import print_function
import datetime

# vars
id_dict = dict()
iso2 = set()
iso3 = set()
seen_ids = set()

# filenames
filename_append = datetime.datetime.now().strftime("%Y-%m-%d")

# open and read seen IMDBids
with open('seen_ids', 'r') as listfile:
    for line in listfile:
        seen_ids.add(line.rstrip())


# open and read dump ISO 2, write IMDBids
with open('dump_ISO-2', 'r') as listfile:
    for line in listfile:
        columns = line.split('\t')
        if len(columns) > 1 and 'de' in columns:
            iso2.add(columns[0])

print ('"de" ids found in ISO-2 file:\t', len(iso2))


# open and read dump ISO 3
counter = 0
with open('dump_ISO-3', 'r') as listfile:
    for line in listfile:
        columns = line.split('\t')
        if len(columns) > 1:
            if 'ger' in columns:
                iso3.add(columns[0])

print ('"ger" ids found in ISO-3 file:\t', len(iso3))


# differences of both sets
print ('union ISO-2 ISO-3:\t\t', len(set.union(iso2, iso3)))
print ('intersection ISO-2 ISO-3:\t', len(set.intersection(iso2, iso3)))
print ('difference ISO-2 ISO-3:\t\t', len(set.difference(iso2, iso3)))


# write union
union = set.union(iso2, iso3)
with open('OS_de-ger_union_IMDBids_' + filename_append, 'w') as destfile:
    for item in union:
        destfile.write(item + "\n")

# seen_ids
counter = 0
with open('new_ids_' + filename_append, 'a') as destfile:
    for item in union:
        if item not in seen_ids:
            destfile.write(item + "\n")
            counter += 1

print ('new ids:\t\t\t', counter)


# open and read movie dump to dict
with open('dump_movies', 'r') as listfile:
    for line in listfile:
        columns = line.split('\t')
        if len(columns) > 1:
            # it's not like they say, we need the OSid and not the IMDBid
            id_dict[columns[1]] = columns[0]


# open and write OSids
with open('OS_de_osid_' + filename_append, 'w') as destfile:
    for item in union:
        if item in id_dict:
            destfile.write(id_dict[item] + '\n')



