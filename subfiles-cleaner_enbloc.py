#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import re
import time
import sys
import codecs

from os import listdir


## TODO:
# file types + unicode ?
# GERMAN
# ª
# Bad ones: 1055792, 770828


# regexes
subnumber = re.compile(r'[0-9]+$')
subtime = re.compile(r'[0-9]{2}\:[0-9]{2}\:[0-9]{1,2}\,[0-9]{3} --> [0-9]{2}\:[0-9]{2}\:[0-9]{1,2}\,[0-9]{2,3}$')
subannounce = re.compile(r'Subtitles downloaded from|\.\.\:\:|Best watched using|CAPTIONING MADE POSSIBLE BY|MGM/UA HOME ENTERTAINMENT INC|Deutsche Untertitel für|SubCentral|tv4user|visit www\.|ripped by|subbed by|Subtitles by|Übersetzt von|Überarbeitet von|Angepasst von|s[0-9]+e[0-9]+', re.IGNORECASE)



# loop through the existing files
for filename in listdir('download/temp/'): # test/ 

    # sanity check on file name
    if re.match(r'IMDBid_[0-9]+$', filename):

        # open and read input file
        with open('download/temp/' + filename, 'r') as f: # test/
            lines = f.read().splitlines()

        # file for cleaned text in write mode 
        cleanedname = filename + '_cleaned'
        try:
            outputfile = open('test/' + cleanedname, 'w')
        except IOError:
            sys.exit ('Could not open output file: ' + cleanedname)

        # buffer necessary to join sentences
        sentence_buffer = ''
        queue = list()
        abbrv_flag = 0
        quote_flag = 0
        flush = 0
        
        # main loop
        for line in lines:

            # skip empty lines
            if line:
            # skip subtitle source announcement
                    # skip subtitles number and times
                    if not subnumber.match(line) and not subtime.match(line) and not subannounce.search(line):
                        # remove diverse tags
                        # str.replace is much faster
                        # if re.search(r'[<>{}]', line):
                        if '<' in line or '{' in line or '>' in line or '}' in line or '~' in line or '[' in line or '#' in line or ']' in line:
                            line = re.sub(r'</?.+?>', '', line)
                            line = re.sub(r'\{[0-9]+\}\{[0-9]+\}', '', line)
                            line = line.replace('o/~', '')
                            line = line.replace('~', '')
                            line = line.replace('[br] ', ' ')
                            for target in ['[', '#', ']']:
                                line = line.replace(target, '')

                        # sentence buffer switch is on
                        if sentence_buffer:
                            sentence_buffer = sentence_buffer + ' ' + line
                        else:
                            sentence_buffer = line


        # write the sentence buffer at the end
        # lookahead and lookbehind: do not split dates : r'.+?(?<![0-9])[.!?](?![0-9\.]+)'
        for sentence in re.findall(r'[A-ZÄÖÜa-zäöü0-9"].+?(?<![0-9])[\.!?]+(?![0-9]+)', sentence_buffer):
            # queue control
            # quotes
            if len(queue) > 0 and quote_flag == 1:
                if re.match(r'"', sentence):
                    queue.append('"') 
                    sentence = re.sub ('^"', '', sentence)
                flush = 1
            # begins with capital letter (most frequent case)
            elif len(queue) > 0 and abbrv_flag == 0 and re.match(r'[A-ZÄÖÜ]', sentence):
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


        # close files
        outputfile.close()



# unicode replacements: does not work
# line = line.replace('Ã¼', 'ü')
# line = re.sub(r'Ã', 'ß', line)
# line = re.sub(r'ÃŒ', 'ü', line)
# line = unicode(line, errors='replace')
