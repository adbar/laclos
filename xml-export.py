#!/usr/bin/python

## export the clean subtitles in XML TEI format


from __future__ import print_function

from os import listdir

from lxml import etree

import codecs
import re


root = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0", encoding="utf-8")
header = etree.SubElement(root, "teiHeader")
text = etree.SubElement(root, "text")

filed = etree.SubElement(header, "fileDesc")
titlestmt = etree.SubElement(filed, "titleStmt")
title_file = etree.SubElement(titlestmt, "title", type="main")

sourced = etree.SubElement(header, "sourceDesc")
titlestmt = etree.SubElement(sourced, "titleStmt")
title = etree.SubElement(titlestmt, "title", type="main")
publistmt = etree.SubElement(sourced, "publicationStmt")
date = etree.SubElement(publistmt, "date")

encodingd = etree.SubElement(header, "encodingDesc")
profiled = etree.SubElement(header, "profileDesc")

body = etree.SubElement(text, "body")

filelist = set()


# loop through the existing files
for filename in listdir('test/'):
    if not re.search(r'.xml$', filename):
        match = re.search(r'IMDBid_([0-9]+)_', filename)
        filelist.add(match.group(1))

# loop through metadata
with open('os_metadata', 'r') as metadatafh:
# with open('testrun', 'r') as metadatafh:
    for entry in metadatafh:
        entry = entry.rstrip()

        # neither json, nor pickle wanted this strings out of the box
        # so basic parsing is an option...
        entry = re.sub('^{|}$', '', entry)
        elements = entry.split(',')
        testdict = dict()
        for e in elements:
            temp = e.split(':')
            try:
                temp[0] = temp[0].replace("'", "")
                temp[1] = temp[1].replace("'", "")
            except IndexError:
                pass
            else:
                testdict[temp[0].strip()] = temp[1].strip()

        if testdict['IDMovieImdb'] in filelist:
            # load metadata
            title.text = testdict['MovieName']
            title_file.text = testdict['SubFileName']
            date = testdict['MovieYear']


        # open and read input file
            with codecs.open('test/' + 'IMDBid_' + testdict['IDMovieImdb'] + '_utf-8_cleaned_sent-split', 'r', 'utf-8') as f:
                body.text = f.read()

                with open('test/' + 'IMDBid_' + testdict['IDMovieImdb'] + '_utf-8_cleaned_sent-split' + '.xml', 'w') as outfh:
                    outfh.write (etree.tostring(root, pretty_print=True, encoding='utf-8'))








