#!/usr/bin/python


from __future__ import print_function

imdb_ids = list()
id_dict = dict()


# open and read list 1
try:
    listfile = open('OS_dump_IMDBid', 'r')
except IOError:
    sys.exit ('Could not open the file containing the inputlist: OS_dump_IMDBid')


# open and write file 2
try:
    defile = open('OS_de_IMDBid', 'w')
except IOError:
    sys.exit ('Could not open the output file: OS_de_IMDBid')


# loop
for line in listfile:
    columns = line.split('\t')
    if 'de' in columns:
        imdb_ids.append(columns[0])
        defile.write(columns[0] + "\n")
listfile.close()
defile.close()


# open and read list 2 -> dict
try:
    listfile = open('OS_dump_export-movie', 'r')
except IOError:
    sys.exit ('Could not open the file containing the inputlist: OS_dump_export-movie')

for line in listfile:
    columns = line.split('\t')
    # it's not like they say, we need the OSid and not the IMDBid
    id_dict[columns[0]] = columns[1]

listfile.close()

# open and write file 2
try:
    defile = open('OS_de_osid', 'w')
except IOError:
    sys.exit ('Could not open the output file: OS_de_osid')

for item in imdb_ids:
    if item in id_dict:
        defile.write(id_dict[item] + '\n')

defile.close()
