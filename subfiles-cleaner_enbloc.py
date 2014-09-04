#!/usr/bin/python
# -*- coding: utf-8 -*-

###	This script is part of LACLOS (https://github.com/adbar/laclos).
###	Copyright (C) Adrien Barbaresi, 2013.


from __future__ import print_function
import re
import time
import sys
import argparse
# import codecs

from os import listdir


## TODO:

# 10208 ?
# whole frame and then filter ?


# argparse
parser = argparse.ArgumentParser()
parser.add_argument('--split-sentences', dest='sentsplit', action="store_true", help='split the sentences')
parser.add_argument('--input-dir', dest='inputdir', help='directory where the input files are', required=True)
parser.add_argument('--output-dir', dest='outputdir', help='directory where the output files are to be stored', required=True)
parser.add_argument('--blacklist', dest='blacklist', help='file containing the blacklist')
parser.add_argument('--xml-output', dest='xmloutput', action="store_true", help='split the sentences')
args = parser.parse_args()


#######

### REGEXES

subnumber = re.compile(r'[0-9]+$')
subtime = re.compile(r'[0-9]{2}\:[0-9]{2}\:[0-9]{1,2}\,[0-9]{2,3} --> [0-9]{2}\:[0-9]{2}\:[0-9]{1,2}\,[0-9]{2,3}')

# 1: match
unwanted1 = re.compile(ur'Subtitles downloaded from|Downloaded From|Best watched using|CAPTIONING MADE POSSIBLE BY|MGM/UA HOME ENTERTAINMENT INC|Deutsche Untertitel|ripped by|subbed by|Sync by|Subtitles by|Transcript by|Thx to|.bersetzung:?|.bersetzt von|.berarbeitet von|Angepasst von|Englische Vorlage von|Resync to|Untertitel:?|Trans[ck]ript:?|Korrektur:?|Synchro:?|Anpassung:?|Produktion:?|Timings:?|original:?|.berarbeitung:?|OCR|Bisher bei|GmbH|Copyright |http://|FPS|We want more|DVD-Untertitel|DVD scripts|T H E|[_+]|-  \|Africa\|  - Bringing|[0-9]\) |in Zusammenarbeit mit$|Eure Anlaufstellen für$|deutsche HQ-Subs.|Normalerweise hat Qualität ihren Preis ...$|doch bei uns kriegt ihr sie umsonst!|taken from', re.IGNORECASE)
# Anlaufstelle für|

# 2: search
unwanted2 = re.compile(ur'www|(sche|für) (HQ-)?Untertitel|German Subtitles|s[0-9]+e[0-9]+|SubCentral|LOST|Staffel [0-9]|Season [0-9]|E N J O Y|\.srt|\.\.::| visit |S u b C e n t r a l . d e|dTV |ripped by|subbed by|Sync by|SD[Il] Media Group|Präsentiert von|Untertitelung|Seite für Untertitel', re.IGNORECASE)

# 3: Editors search (Regexes by Berthold Ulreich)
unwanted3 = re.compile(ur'willow|staubsauger|datai|maone|angeldream|arigold|buffy2500|dreumex|randall flagg|där fürst|riorizor|mosfilm|sdi media group|zerocl|deepthought42|charlie°|dehoh|urgh! argh|kakarott|crazy.nugget|tv4u|germansubs|opensubtitles|visiontext|tv4user|cimbom1905|maexchen|tvfreaks|delabambi|kristin gerdes|titra-wien|anke watson|fatbrat|velious|siralos|threepwood|zerotollerance|german sdh|eggmaster|mardermann|vicomedia|asenkerschbaumer|hörgeschädigte|gelula|schoker88|staubsauger1000|dagorcai|juppjulasch|subnews|fansub|arigold|wieni07|dagorcai|lord-homer|kezia|l1nk|setup1503|melsmiley|3xtrem3|para\.llax|phiber|jazzhead|ycheah|geysir|cyoo|siralos|revan|schoker|tngs|blubmöp|doggydog|nub4u|swini|ooinsaneoo|redfox|knochenbein|schnapsteufel|lamodus|anddro\+', re.IGNORECASE)

# 4: Rest search (Regexes by Berthold Ulreich)
unwanted4 = re.compile(ur'(bisher|zuvor|zuletzt)\s(bei|auf)|was bisher geschah', re.IGNORECASE)

# _ ?
# _ _ / _ _
# FREMDSPRACHE ?
# lnstrumentalmusik im Hintergrund

## Regexes by Berthold Ulreich
#ur'(angepasst|anpassung)([/:]|\s(von|durch)|)',
#ur'(korrektur|korrigiert|deutsch|untertitel)([/:]|</?[^<>]+>|\s(von|durch))',
#ur'überarbeit(et|ung)([/:]|\s(von|durch)|)',
#r'(rip|sub|synch?ro|syncroni[sz]ed|sync|transcript|conformed|caption(s|ing))([:/]|\sby)',
#r'^subti?t?l?e?s?$',
#r'^[a-z]$',
#r'=+-+',
#ur'präsentiert([:]|\svon)',
#ur'(=+-+=*|=*-+=+)\s+präsentiert',
#ur'präsentiert\.\.\.+',
#ur'<i>¶|¶</i>',
#r'~',
# e-mail Addressen
# r'divx|xvid',
# ur'für\swww\S+\.de',
# r'\]\[[^\]\[]+\]\[',
#r'u[ks]-serien',
#r'::+',
#ur'©|\(c\)',
#r'original:',
#r'(drehbuch|regie|text|produ[ck]tion|synch?ronisation)(:|\svon)',
#ur'°\.°',
#r'german',
#r'[0-9][0-]/[0-9][0-9][0-9][0-9]',
#r'hr\.pdtv',
#ur'^für$',

#######


# process blacklist
blacklist = set()
if args.blacklist:
    with open(args.blacklist, 'r') as blackfh:
        blacklist = blackfh.read().splitlines()


# loop through the existing files
for filename in listdir(args.inputdir): #  test/ korpus/test/

    # sanity check on file name
    filecheck = re.compile(r'IMDBid_([0-9]+)_utf-8$')
    if filecheck.match(filename):

        # skip if the file has been blacklisted
        if filecheck.match(filename).group(1) in blacklist:
            continue

        # open and read input file
        with open(args.inputdir + filename, 'r') as f: #  test/ korpus/test/
            lines = f.read().splitlines()

        # file for cleaned text in write mode
        if args.sentsplit:
            cleanedname = filename + '_cleaned_sent-split'
        else:
            cleanedname = filename + '_cleaned_bare-lines'
        try:
            outputfile = open(args.outputdir + cleanedname, 'w') # test/
            # outputfile = codecs.open('test/' + cleanedname, encoding='utf-8', mode='w')
        except IOError:
            sys.exit ('Could not open output file: ' + cleanedname)

        # buffer necessary to join sentences
        sentence_buffer = ''
        clean_lines = list()
        queue = list()
        abbrv_flag = 0
        quote_flag = 0
        upper_flag = 0
        flush = 0
        
        # main loop

        # text type
        try:
            # MicroDVD
            if re.match(r'\{[0-9]+\}\{[0-9]+\}', lines[5]):
                texttype = 1
            # SubViewer
            elif re.match(r'\[[A-Z]+\]', lines[5]):
                texttype = 2
            # SAMI
            elif re.match(r'<SAMI>', lines[0]):
                texttype = 3
                sami_flag = 0
            # SSA
            elif re.match(r'﻿\[Script Info\]', lines[0]):
            # elif re.search(r'﻿﻿[a-z]', lines[0]):
                texttype = 4
            # default
            else:
                texttype = 0
        except IndexError:
            print ('Empty file ?', filename)
            continue

        print (filename, lines[0], texttype, sep='\t')

        for line in lines:

            # skip empty lines
            if line:

                # MicroDVD
                if texttype == 1:
                    line = re.sub(r'\{[0-9]+\}\{[0-9]+\}', '', line)
                    line = re.sub(r'\{.+?\}', '', line)
                    line = line.replace('|', ' ')
                # SubViewer
                elif texttype == 2:
                    if re.match (r'[0-9]{2}\:[0-9]{2}\:[0-9]{2}\.[0-9]{2},[0-9]{2}\:[0-9]{2}\:[0-9]{2}\.[0-9]{2}', line) or re.match(r'\[[A-Z ]+\]', line):
                        # line = ''
                        continue
                # SAMI
                elif texttype == 3:
                    if sami_flag == 0:
                        if re.match(r'<BODY>', line):
                            sami_flag = 1
                        # line = ''
                        continue
                    else:
                        line = re.sub(r'</?.+?>', ' ', line)
                        line = line.replace('&nbsp;', ' ')
                        line = line.replace('&auml;', 'ä')
                        line = line.replace('&uuml;', 'ü')
                        line = line.strip(' ')

                # SSA
                elif texttype == 4:
                    if not re.match(r'Dialogue: ', line):
                        # print (line)
                        # line = ''
                        continue
                    elif re.search(r'SYNAPSE  pxxx', line):
                        continue
                    else:
                        line = re.sub(r'Dialogue:.+?0,,', '', line)
                        # Dialogue: Marked=0,0:01:33.47,0:01:37.47,Default,NTP,0000,0000,0000,!Effect,
                        # print (line)
                        line = re.sub(r'Dialogue:.+?Effect,', '', line)
                        line = line.replace('\N', ' ')
                        line = line.replace('\\n', ' ')
                        line = re.sub(r'\{.+?\}', '', line)

                # skip subtitle source announcement
                # skip subtitles number and times
                # skip lines where there are more non-word characters than word characters
                if not subnumber.match(line) and not subtime.match(line) and not unwanted1.match(line) and not unwanted2.search(line) and not unwanted3.search(line) and not unwanted4.search(line) and not len(re.findall(r'[^\w\s]', line)) > len(re.findall(r'[\w\s]', line)) and not len(re.findall(r'[\s]', line)) >= len(re.findall(r'[\w]', line)):

                    # remove diverse tags
                    # str.replace is much faster
                    # if re.search(r'[<>{}]', line):
                    if '<' in line or '>' in line or '~' in line or '[' in line or ']' in line or '(' in line or ')' in line or '#' in line:
                        line = re.sub(r'</?.+?>', '', line)
                        line = line.replace('o/~', '')
                        line = line.replace('~', '')
                        line = line.replace('[br]', ' ')
                        line = line.replace('#', '')
                        ## regex replace: [] and ()
                        if args.xmloutput:
                            line = re.sub(r'[\[\(](.+?)[\)\]]', r'<s type="other">\1</s>', line)
                        else:
                            line = line.replace('[', '')
                            line = line.replace(']', '')
                            line = line.replace('(', '')
                            line = line.replace(')', '')


                    if texttype != 3 and re.match(r'[A-ZÄÖÜ ]+$', line):
                        line = line + ' .'

                    # strip spaces
                    line = re.sub(r'\s+', ' ', line)
                    line = line.strip()

                    if args.sentsplit:
                        # sentence buffer switch is on
                        if line:
                            if sentence_buffer:
                                sentence_buffer = sentence_buffer + ' ' + line
                            else:
                                sentence_buffer = line
                    else:
                        clean_lines.append(line)

        if args.sentsplit:
            # write the sentence buffer at the end
            # lookahead and lookbehind: do not split dates : r'.+?(?<![0-9])[.!?](?![0-9\.]+)'
            for sentence in re.findall(r'[A-ZÄÖÜa-zäöü0-9"].+?(?<![0-9])[\.!\?]+(?![0-9]+)', sentence_buffer):

                # queue control
                # quotes
                if queue:
                    if quote_flag == 1:
                        if re.match(r'"', sentence):
                            queue.append('"') 
                            sentence = re.sub ('^"', '', sentence)
                        flush = 1
                    # begins with capital letter (most frequent case)
                    elif abbrv_flag == 0 and re.match(r'[A-ZÄÖÜ]', sentence):
                        flush = 1
                    else:
                        flush = 0

                # flush the queue
                if flush == 1:
                    for item in queue:
                        outputfile.write(item)
                    outputfile.write('\n')
                    queue = []

                # sentence tests
                if not unwanted1.match(sentence) and not unwanted2.search(sentence) and not len(re.findall(r'[^\w\s]', sentence)) > len(re.findall(r'[\w\s]', sentence)) and not len(re.findall(r'[\s]', sentence)) >= len(re.findall(r'[\w]', sentence)):

                    # if quote count is not even
                    if sentence.count('"') % 2 != 0:
                        queue.append(sentence.lstrip())
                        quote_flag = 1
                    else:
                        quote_flag = 0

                    # avoid breaking at A. or B. or Mr./Ms./Dr. XX or St., or at '...' at the beginning of a sentence
                    if re.search(r'[A-Z]\.$', sentence) or re.search(r'[MD][Rrs]\.$|Mrs\.$', sentence) or re.search(r'St\.$', sentence):
                        queue.append(sentence.lstrip() + ' ')
                        abbrv_flag = 1
                    else:
                        if abbrv_flag == 1:
                            abbrv_flag = 0
                        queue.append(sentence.lstrip())


            # no one left behind
            match = re.search(r'[\.!?]([^\.?!]+?)$', sentence_buffer)
            if match:
                outputfile.write(match.group(1).lstrip() + '\n')

        # if not split: join the list and print it
        else:
            outputfile.write('\n'.join(clean_lines))


        # close files
        outputfile.close()

