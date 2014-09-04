#!/usr/bin/python3

# purpose: filter subtitles based on language check results
# Python3 compatible


badones = list()

with open('langstat-summary', 'r') as summaryfh:
    # skip first line
    next(summaryfh)
    for line in summaryfh:
        columns = line.split('\t')
        if float(columns[1]) > 50 or float(columns[2]) < 20 : # or columns[3] is not 'de'
            badones.append(int(columns[0]))

badones.sort()

with open('bad-ones', 'w') as badonesfh:
    for item in badones:
        badonesfh.write(str(item) + '\n')