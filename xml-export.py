#!/usr/bin/python

###	This script is part of LACLOS (https://github.com/adbar/laclos).
###	Copyright (C) Adrien Barbaresi, 2013.
###	This is free software, licensed under the GNU Lesser General Public License (https://www.gnu.org/licenses/lgpl.html)


## export the clean subtitles in XML TEI format with the metadata collected from the XMLRPC queries


from __future__ import print_function
from os import listdir
from lxml import etree

import argparse
import codecs
import re


## TODO:
# genre ?


## argparse
parser = argparse.ArgumentParser()
parser.add_argument('--inputdir', dest='inputdir', help='directory where the files are to be found', required=True)
parser.add_argument('--outputdir', dest='outputdir', help='directory where the files are to be written', required=True)
args = parser.parse_args()


## XML scheme

# header
root = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0", encoding="utf-8")
header = etree.SubElement(root, "teiHeader")

# fileDesc
filed = etree.SubElement(header, "fileDesc")
titlestmt1 = etree.SubElement(filed, "titleStmt")
title1 = etree.SubElement(titlestmt1, "title")
fileeditor = etree.SubElement(titlestmt1, "editor")
persname1 = etree.SubElement(fileeditor, "persName")
surname = etree.SubElement(persname1, "surname")
forename = etree.SubElement(persname1, "forename")
surname.text = "Barbaresi"
forename.text = "Adrien"
resp = etree.SubElement(filed, "respStmt")
org = etree.SubElement(resp, "orgName")
org.text = "Berlin-Brandenburgische Akademie der Wissenschaften"

# sourceDesc
sourced = etree.SubElement(header, "sourceDesc")
titlestmt2 = etree.SubElement(sourced, "titleStmt")
title = etree.SubElement(titlestmt2, "title", type="main")
titlerel = etree.SubElement(titlestmt2, "title", type="release")
title_file = etree.SubElement(titlestmt2, "title", type="file")
editor = etree.SubElement(titlestmt2, "editor")
persname = etree.SubElement(editor, "persName")
nickname = etree.SubElement(persname, "nickname")
rank = etree.SubElement(persname, "rank")
series = etree.SubElement(titlestmt2, "seriesStmt")
season = etree.SubElement(series, "season")
episode = etree.SubElement(series, "episode")

publistmt = etree.SubElement(sourced, "publicationStmt")
datefilm = etree.SubElement(publistmt, "date", type="film publication")
datepub = etree.SubElement(publistmt, "date", type="subtitle publication")
url = etree.SubElement(publistmt, "url", type="web page URL")
fileurl = etree.SubElement(publistmt, "url", type="file URL")
imdbid = etree.SubElement(publistmt, "idno", type="IMDB id")

# encodingDesc
encodingd = etree.SubElement(header, "encodingDesc")

# profileDesc
profiled = etree.SubElement(header, "profileDesc")
textclass = etree.SubElement(profiled, "textClass")
filmrating = etree.SubElement(textclass, "rating", type="film")
subrating = etree.SubElement(textclass, "rating", type="subtitles")
kind = etree.SubElement(textclass, "kind")

# text & body
text = etree.SubElement(root, "text")
body = etree.SubElement(text, "body")

filelist = set()


# loop through the existing files
for filename in listdir(args.inputdir):
    if not re.search(r'.xml$', filename) and not re.search(r'_stats$', filename):
        match = re.match(r'IMDBid_([0-9]+)_', filename)
        if match:
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
            temp = e.split(': ')
            try:
                temp[0] = temp[0].replace("'", "")
                temp[1] = temp[1].replace("'", "")
            except IndexError:
                pass
            else:
                testdict[temp[0].strip()] = temp[1].strip()

        if testdict['IDMovieImdb'] in filelist:
            ## load metadata
            imdbid.text = testdict['IDMovieImdb']
            # titles
            title1.text = testdict['MovieName']
            title.text = testdict['MovieName']
            titlerel.text = testdict['MovieReleaseName']
            title_file.text = testdict['SubFileName']
            # dates
            datefilm.text = testdict['MovieYear']
            datepub.text = testdict['SubAddDate']
            # urls
            # /sid-gasek0lvm1f29pdrnsdce6ljn7'
            urltxt = re.sub('/sid-.+$', '', testdict['SubtitlesLink'])
            fileurltxt = re.sub('/sid-.+$', '', testdict['SubDownloadLink'])
            url.text = urltxt
            fileurl.text = fileurltxt
            # editor
            nickname.text = testdict['UserNickName']
            rank.text = testdict['UserRank']
            # series
            season.text = testdict['SeriesSeason']
            episode.text = testdict['SeriesEpisode']
            # classification
            filmrating.text = testdict['MovieImdbRating']
            filmrating.text = testdict['SubRating']
            kind.text = testdict['MovieKind']


            # open and read input file
            # '_utf-8_cleaned_sent-split'
            with codecs.open(args.inputdir + 'IMDBid_' + testdict['IDMovieImdb'] + '_utf-8_cleaned_bare-lines', 'r', 'utf-8') as f:
                try:
                    body.text = f.read()
                except ValueError:
                    print ('Problem with file: IMDBid_' + testdict['IDMovieImdb'])

                # '_utf-8_cleaned_sent-split'
                with open(args.outputdir + 'IMDBid_' + testdict['IDMovieImdb'] + '_utf-8_cleaned_bare-lines' + '.xml', 'w') as outfh:
                    outfh.write (etree.tostring(root, xml_declaration=True, pretty_print=True, encoding='utf-8'))


