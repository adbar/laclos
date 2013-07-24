#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import re
import time
import sys
import codecs

from os import listdir


## TODO:
# ... XX problem
# GERMAN
# ª
# Bad ones: 1055792, 770828


# regexes
subnumber = re.compile(r'[0-9]+$')
subtime = re.compile(r'[0-9]{2}\:[0-9]{2}\:[0-9]{1,2}\,[0-9]{3} --> [0-9]{2}\:[0-9]{2}\:[0-9]{1,2}\,[0-9]{2,3}$')
subannounce = re.compile(r'Subtitles downloaded from|\.\.\:\:|Best watched using|CAPTIONING MADE POSSIBLE BY|MGM/UA HOME ENTERTAINMENT INC|Deutsche Untertitel für|SubCentral|tv4user|visit www\.|ripped by|subbed by|Subtitles by|Übersetzt von|Überarbeitet von|Angepasst von|s[0-9]+e[0-9]+', re.IGNORECASE)



# loop through the existing files
for filename in listdir('test/'): # download/temp/

    # sanity check on file name
    if re.match(r'IMDBid_[0-9]+$', filename):

        # open and read input file
        try:
            inputfile = open('test/' + filename, 'r') #download/temp/
        except IOError:
            sys.exit ('Could not open input file: ' + filename)

        # file for cleaned text in write mode 
        cleanedname = filename + '_cleaned'
        try:
            outputfile = open('test/' + cleanedname, 'w')
        except IOError:
            sys.exit ('Could not open output file: ' + cleanedname)

        # buffer necessary to join sentences
        sentence_buffer = ''
        queue = list()
        flag = 0

        # main loop
        for line in inputfile:

            # strip \newline
            line = line.rstrip()

            # skip empty lines
            if len(line) > 0:
            # skip subtitle source announcement
                    # skip subtitles number and times
                    if not subnumber.match(line) and not subtime.match(line) and not subannounce.search(line):
                            # remove diverse tags
                            # str.replace is much faster
                            if re.search(r'[<>{}]', line): #if char in string ?
                                line = re.sub(r'</?.+?>', '', line)
                                line = re.sub(r'\{[0-9]+\}\{[0-9]+\}', '', line)
                            line = line.replace('[br] ', ' ')
                            line = line.replace('o/~', '')
                            # line = re.sub(r'[#~\[\]]+', '', line)
                            for char in ['#', '~', '[', ']']:
                                if char in line:
                                    line = line.replace(char, '')

                            # sentence buffer switch is on
                            if len(sentence_buffer) > 0:
                                sentence_buffer = sentence_buffer + ' ' + line
                            else:
                                sentence_buffer = line


        # write the sentence buffer at the end
        # lookahead and lookbehind: do not split dates : r'.+?(?<![0-9])[.!?](?![0-9\.]+)'
        for sentence in re.findall(r'[A-ZÄÖÜ0-9].+?(?<![0-9])[.!?]+(?![0-9]+)', sentence_buffer):
            # queue control
            if len(queue) > 0 and flag == 0: 
                if re.match(r'[A-ZÄÖÜ]', sentence):
                    # flush queue
                    for item in queue:
                        outputfile.write(item)
                    outputfile.write('\n')
                    queue = []

            if not subannounce.search(sentence):
                # avoid breaking at A. or B. or Mr./Ms./Dr. XX or St., or at '...' at the beginning of a sentence
                if re.search(r'[A-Z]\.$', sentence) or re.search(r'[MD][Rrs]\.$|Mrs\.$', sentence) or re.search(r'St\.$', sentence):
                    queue.append(sentence.lstrip() + ' ')
                    flag = 1
                else:
                    if flag == 1:
                        queue.append(sentence.lstrip())
                        flag = 0
                    else:
                        outputfile.write(sentence.lstrip() + '\n')
                # no one left behind
                #match = re.search(r'[.!?]([^.!?]+?)$', sentence)
                #if match:
                #    queue.append(match.group(1).lstrip())


        # no one left behind
        match = re.search(r'[.!?]([^.!?]+?)$', sentence_buffer)
        if match:
            outputfile.write(match.group(1).lstrip() + '\n')


        # close files
        inputfile.close()
        outputfile.close()


# or re.search(r'\.{2,3}$', sentence)




# sentence splitting (lookbehind: do not split quotes)
# if re.search(r'[.!?](?! ?")', sentence_buffer):

                            # unicode replacements: does not work
                            # line = line.replace('Ã¼', 'ü')
                            # line = re.sub(r'Ã', 'ß', line)
                            # line = re.sub(r'ÃŒ', 'ü', line)
                            # line = unicode(line, errors='replace')
