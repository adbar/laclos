#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import re
import time
import sys
import argparse
# import codecs

from os import listdir


## TODO:
# texttype [Script Info] problem: 1890383
# 99669 quotes problem

# unicode ?
# GERMAN
# ª
# Bad ones: 1055792, 770828


# argparse
parser = argparse.ArgumentParser()
parser.add_argument('--split-sentences', dest='sentsplit', action="store_true", help='split the sentences')
args = parser.parse_args()



# regexes
subnumber = re.compile(r'[0-9]+$')
subtime = re.compile(r'[0-9]{2}\:[0-9]{2}\:[0-9]{1,2}\,[0-9]{2,3} --> [0-9]{2}\:[0-9]{2}\:[0-9]{1,2}\,[0-9]{2,3}')
subannounce = re.compile(r'Subtitles downloaded from|\.\.\:\:|Best watched using|CAPTIONING MADE POSSIBLE BY|MGM/UA HOME ENTERTAINMENT INC|Deutsche Untertitel für|SubCentral|tv4user|visit www\.|ripped by|subbed by|Subtitles by|Übersetzt von|Überarbeitet von|Angepasst von|Untertitel:|s[0-9]+e[0-9]+|^OCR', re.IGNORECASE)



# loop through the existing files
for filename in listdir('download/test/'): #  test/

    # sanity check on file name
    if re.match(r'IMDBid_[0-9]+$', filename):

        # open and read input file
        with open('download/test/' + filename, 'r') as f: #  test/
            lines = f.read().splitlines()

        # file for cleaned text in write mode
        if args.sentsplit:
            cleanedname = filename + '_cleaned_sent-split'
        else:
            cleanedname = filename + '_cleaned_bare-lines'
        try:
            outputfile = open('test/' + cleanedname, 'w')
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
                texttype = 4
            # default
            else:
                texttype = 0
        except IndexError:
            print (filename)
            continue

        # print (filename, lines[0], texttype, sep='\t')

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
                        line = ''
                        # continue
                # SAMI
                elif texttype == 3:
                    if sami_flag == 0:
                        if re.match(r'<BODY>', line):
                            sami_flag = 1
                        line = ''
                        # continue
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
                        line = ''
                    else:
                        line = re.sub(r'Dialogue:.+?0,,', '', line)
                        # Dialogue: Marked=0,0:01:33.47,0:01:37.47,Default,NTP,0000,0000,0000,!Effect,
                        # print (line)
                        line = re.sub(r'Dialogue:.+?Effect,', '', line)
                        line = line.replace('\N', ' ')
                        line = re.sub(r'\{.+?\}', '', line)

                # skip subtitle source announcement
                # skip subtitles number and times
                if not subnumber.match(line) and not subtime.match(line) and not subannounce.search(line):

                    # remove diverse tags
                    # str.replace is much faster
                    # if re.search(r'[<>{}]', line):
                    if '<' in line or '>' in line or '~' in line or '[' in line or ']' in line or '(' in line or ')' in line or '#' in line:
                        line = re.sub(r'</?.+?>', '', line)
                        line = line.replace('o/~', '')
                        line = line.replace('~', '')
                        line = line.replace('[br]', ' ')
                        line = line.replace('[', '')
                        line = line.replace(']', '')
                        line = line.replace('(', '')
                        line = line.replace(')', '')
                        line = line.replace('#', '')

                    if texttype != 3 and re.match(r'[A-ZÄÖÜ ]+$', line):
                        line = line + ' .'


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
                if not subannounce.search(sentence):

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

