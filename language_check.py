#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import re
import time
import sys
import argparse
# import codecs

from os import listdir

from enchant.checker import SpellChecker
spellcheck_de = SpellChecker("de_DE")
spellcheck_us = SpellChecker("en_US")


## TODO:
# Bad ones: 1055792, 770828



# argparse
# parser = argparse.ArgumentParser()
# parser.add_argument('--split-sentences', dest='split', action="store_true", help='split the sentences')
# args = parser.parse_args()



# vars
wcounts = list()
de_errs = list()
us_errs = list()
de_stat = list()
de_values = dict()


# loop through the existing files
for filename in listdir('test_langid/'):

    # sanity check on file name
    if re.match(r'IMDBid_[0-9]+_', filename) and not re.match(r'stats', filename):

        # open and read input file
        with open('test_langid/' + filename, 'r') as f:
            lines = f.read().splitlines()

        # file for cleaned text in write mode
        statsfile = filename + '_stats'
        try:
            statsfh = open('test_langid/' + statsfile, 'w')
        except IOError:
            sys.exit ('Could not open output file: ' + cleanedname)
        
        # main loop
        for line in lines:

            # Check spelling to see if the link text is in English
            langtest = re.sub(r'[^\w\s]', '', line)
            wordcount = len(re.findall(r'\w+', langtest)) # redundant, see enchant.tokenize
            de_errcount = 0
            try:
                spellcheck_de.set_text(langtest)
                for err in spellcheck_de:
                    de_errcount += 1
            # the length of body has been checked, so that means it contained only punctuation marks
            except ZeroDivisionError:
                flag = 1
            # if the string couldn't be translated properly, it is also interesting
            except (UnicodeEncodeError, AttributeError):
                 flag = 1

            us_errcount = 0
            try:
                spellcheck_us.set_text(langtest)
                for err in spellcheck_us:
                    us_errcount += 1
            # the length of body has been checked, so that means it contained only punctuation marks
            except ZeroDivisionError:
                flag = 1
            # if the string couldn't be translated properly, it is also interesting
            except (UnicodeEncodeError, AttributeError):
                flag = 1

            statsfh.write (str(wordcount)  + '\t{0:.1f}' . format((de_errcount / wordcount) * 100) + '\t')
            statsfh.write ('{0:.1f}' . format((us_errcount / wordcount) * 100) + '\n')

            wcounts.append(wordcount)
            de_errs.append(de_errcount)
            us_errs.append(us_errcount)

        de_mean = (sum(de_errs) / sum(wcounts) * 100)

        statsfh.write ('Mean words per line: {0:.1f}' . format(sum(wcounts) / len(wcounts)) + '\n')
        statsfh.write ('Mean DE errors: {0:.1f}' . format(sum(de_errs) / len(de_errs)) + '\n')
        statsfh.write ('% DE errors per word: {0:.1f}' . format(de_mean) + '\n')
        statsfh.write ('Mean US errors: {0:.1f}' . format(sum(us_errs) / len(us_errs)) + '\n')
        statsfh.write ('% US errors per word: {0:.1f}' . format((sum(us_errs) / sum(wcounts)) * 100) + '\n')
        
        statsfh.close()

        de_stat.append (de_mean)

        # get text id from file name (there should not be any error here)
        match = re.search('([0-9]+)', filename)
        textid = match.group(1)

        # store text id and mean DE errors
        de_values[textid] = de_mean



# print DE_mean digest values
i = 0
for item in sorted(de_values, key=de_values.get, reverse=True):
    print (item, '{0:.1f}' . format(de_values[item]), sep='\t')
    i += 1
    #if i >= 5:
    #    break


