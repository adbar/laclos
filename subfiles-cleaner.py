#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import re
import time
import sys

from os import listdir


# regexes
subnumber = re.compile(r'[0-9]+$')
subtime = re.compile(r'[0-9]{2}\:[0-9]{2}\:[0-9]{2}\,[0-9]{3} --> [0-9]{2}\:[0-9]{2}\:[0-9]{2}\,[0-9]{3}$')
subannounce = re.compile(r'Subtitles downloaded from|..::|Best watched using')


# loop through the existing files
for filename in listdir('test/'):

    # sanity check on file name
    if re.match(r'IMDBid_[0-9]+$', filename):

        # open and read input file
        try:
            inputfile = open('test/' + filename, 'r')
        except IOError:
            sys.exit ('Could not open input file: ' + filename)

        # file for cleaned text in write mode 
        cleanedname = filename + '_cleaned'
        try:
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
            #    try:
            #        line = line.encode('iso-8859-15')
            #    except UnicodeDecodeError:
            #        pass
            

            # skip empty lines
            if len(line) > 0:
                # skip subtitles number and times
                if not subnumber.match(line) and not subtime.match(line):
                    # skip subtitle source announcement
                    if not subannounce.search(line):
                        line = re.sub(r'</?i>', '', line)

                        # sentence buffer switch is on
                        if len(sentence_buffer) > 0:
                            # append only if the next line does not start with a capital letter
                            if re.match(r'[a-z]', line) or re.search(r',$', sentence_buffer):
                                sentence_buffer = sentence_buffer + ' ' + line
                            # write the sentence buffer
                            else:
                                outputfile.write(sentence_buffer.lstrip() + '\n')
                                sentence_buffer = ''
                                # line buffering for the rest
                                if len(line_buffer) > 0:
                                    line_buffer = line_buffer + ' ' + line
                                else:
                                    line_buffer = line

                        # normal case
                        else:
                            if len(line_buffer) > 0:
                                line_buffer = line_buffer + ' ' + line
                            else:
                                line_buffer = line
                
                # write the line buffer and reset it
                else:
                    if len(line_buffer) > 0:
                        # sentence splitting (lookahaed and lookbehind: do not split dates)
                        if re.search(r'[.!?]', line_buffer):
                            for sentence in re.findall(r'.+?(?<![0-9])[.!?](?![0-9\.]+)', line_buffer):
                                # avoid breaking at Mr. XX or at '...' at the beginning of a sentence
                                if re.search(r'Mr\.$', sentence) or re.match(r'\.\.\.', sentence):
                                    outputfile.write(sentence.lstrip() + ' ')
                                else:
                                    outputfile.write(sentence.lstrip() + '\n')
                            # no one left behind
                            match = re.search(r'[.!?]([^.!?]+?)$', line_buffer)
                            if match:
                                outputfile.write(match.group(1) + '\n')
                        else:
                            outputfile.write(line_buffer + '\n')

                        line_buffer = ''


        # print last line ?
        if len(line_buffer) > 0:
            outputfile.write(line_buffer.lstrip() + '\n')

        # close files
        inputfile.close()
        outputfile.close()

