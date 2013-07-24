#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import re
import time
import sys
import codecs

from os import listdir


## TODO:
# cut all sentences at the end of a text ?
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
            #inputfile = codecs.open('test/' + filename, 'r', encoding='latin_1')
            inputfile = open('test/' + filename, 'r') #download/temp/
        except IOError:
            sys.exit ('Could not open input file: ' + filename)

        # file for cleaned text in write mode 
        cleanedname = filename + '_cleaned'
        try:
            #outputfile = codecs.open('test/' + cleanedname, 'w', encoding='utf8')
            outputfile = open('test/' + cleanedname, 'w')
        except IOError:
            sys.exit ('Could not open output file: ' + cleanedname)

        # buffers necessary to join sentences
        line_buffer = ''
        sentence_buffer = ''

        # main loop
        for line in inputfile:

            # strip \newline
            line = line.rstrip()
            # encoding
            #try:
            #    line = line.encode('utf-8')
            #except UnicodeDecodeError:
                #print (line)
                #pass
            

            # skip empty lines
            if len(line) > 0:
            # skip subtitle source announcement
                if not subannounce.search(line):
                    # skip subtitles number and times
                    if not subnumber.match(line) and not subtime.match(line):
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

                            # unicode replacements: does not work
                            # line = line.replace('Ã¼', 'ü')
                            # line = re.sub(r'Ã', 'ß', line)
                            # line = re.sub(r'ÃŒ', 'ü', line)
                            # line = unicode(line, errors='replace')

                            # sentence buffer switch is on
                            # append only if the next line does not start with a capital letter
                            if re.match(r'[a-z]', line) or re.search(r',$', sentence_buffer):
                                sentence_buffer = sentence_buffer + ' ' + line
                            # write the sentence buffer
                            else:
                                if len(sentence_buffer) > 0:
                                    outputfile.write(sentence_buffer.lstrip() + '\n')
                                    sentence_buffer = ''
                                # line buffering for the rest
                                if len(sentence_buffer) > 0:
                                    sentence_buffer = sentence_buffer + ' ' + line
                                else:
                                    sentence_buffer = line
                
                    # write the line buffer and reset it
                    else:
                        #if len(line_buffer) > 0:
                        if len(sentence_buffer) > 0:
                            # sentence splitting (lookbehind: do not split quotes)
                            if re.search(r'[.!?](?! ?")', line):
                                # lookahead and lookbehind: do not split dates
                                for sentence in re.findall(r'.+?(?<![0-9])[.!?](?![0-9\.]+)', line):
                                    # avoid breaking at A. or B. or Mr./Ms./Dr. XX or St., or at '...' at the beginning of a sentence
                                    if re.search(r'[A-Z]\.$', sentence) or re.search(r'[MD][Rrs]\.$|Mrs\.$', sentence) or re.search(r'St\.$', sentence) or re.match(r'\.+', sentence):
                                        outputfile.write(sentence.lstrip() + ' ')
                                    else:
                                        outputfile.write(sentence.lstrip() + '\n')
                                # no one left behind
                                match = re.search(r'[.!?]([^.!?]+?)$', line_buffer)
                                if match:
                                    sentence_buffer = sentence_buffer + ' ' + match.group(1)


        # print last line ?
        # if len(line_buffer) > 0:
        if len(sentence_buffer) > 0 and not subannounce.search(sentence_buffer):
            outputfile.write(sentence_buffer.lstrip() + '\n')

        # close files
        inputfile.close()
        outputfile.close()

