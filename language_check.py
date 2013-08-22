#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import re
import time
import sys
import argparse

from os import stat
from os import listdir

from enchant.checker import SpellChecker
spellcheck_de = SpellChecker("de_DE")
spellcheck_us = SpellChecker("en_US")

import langid


## TODO:
# python 3 ?


# argparse
parser = argparse.ArgumentParser()
parser.add_argument('--line-by-line', dest='linebyline', action="store_true", help='apply language id line by line (much slower)')
parser.add_argument('-d', '--dir', dest='dir', help='directory where the files are', required=True)
parser.add_argument('-n', '--numval', dest='numval', help='number of best/worst values to show (defaults to 10)')
args = parser.parse_args()

if not args.numval:
    args.numval = 10

# vars
wcounts, de_errs, us_errs, de_stat = (list() for i in range(4))
de_values, us_values, langid_results = (dict() for i in range(3))


def spellcheck_de_us(langtest):

    # spellcheck DE + US
    global de_errcount, us_errcount, flag, langidresult
    de_errcount = 0
    us_errcount = 0
    try:
        spellcheck_de.set_text(langtest)
        for err in spellcheck_de:
            de_errcount += 1
        spellcheck_us.set_text(langtest)
        for err in spellcheck_us:
            us_errcount += 1
    # if the string couldn't be translated properly, it is also interesting
    except (UnicodeEncodeError, AttributeError):
        flag = 1

    # langid.py
    # langidresult = langid.classify(langtest)


# loop through the existing files
for filename in listdir(args.dir): # test_langid/ korpus/test/

    # sanity check on file name + size (utf-8 ?)
    if re.match(r'IMDBid_[0-9]+_', filename) and not re.search(r'stats', filename) and not stat(args.dir + filename)[6] == 0:

        # open and read input file
        with open(args.dir + filename, 'r') as f:	# test_langid/ korpus/test/
            lines = f.read().splitlines()

        # file for cleaned text in write mode
        statsfile = filename + '_stats'
        try:
            statsfh = open(args.dir + statsfile, 'w') # test_langid/ korpus/test/
        except IOError:
            sys.exit ('Could not open output file: ' + cleanedname)
        
        # main loop
        whole_text = ''
        for line in lines:

            line = line.rstrip()
            flag = 0
            whole_text += " " + line

            if args.linebyline:

                # Check spelling to see if the link text is in English
                langtest = re.sub(r'[^\w\s]', '', line)
                wordcount = len(re.findall(r'\w+', langtest)) # redundant, see enchant.tokenize ?

                if wordcount > 0:

                    spellcheck_de_us(langtest)
                    langidresult = langid.classify(line)

                    # stats
                    statsfh.write (str(wordcount) + '\t{0:.1f}' . format((de_errcount / wordcount) * 100) + '\t')
                    statsfh.write ('{0:.1f}' . format((us_errcount / wordcount) * 100) + '\t' + str(flag) + '\t')
                    statsfh.write (str(langidresult[0]) + '\t{0:.1f}' . format(langidresult[1]) + '\n')

                    wcounts.append(wordcount)
                    de_errs.append(de_errcount)
                    us_errs.append(us_errcount)

        # separate processing
        if args.linebyline:
            de_mean = (sum(de_errs) / sum(wcounts)) * 100
            us_mean = (sum(us_errs) / sum(wcounts)) * 100
            statsfh.write ('Mean words per line: {0:.1f}' . format(sum(wcounts) / len(wcounts)) + '\n')
            statsfh.write ('Mean DE errors: {0:.1f}' . format(sum(de_errs) / len(de_errs)) + '\n')
            statsfh.write ('Mean US errors: {0:.1f}' . format(sum(us_errs) / len(us_errs)) + '\n')
        else:
            langtest = re.sub(r'[^\w\s]', '', whole_text)
            wordcount = len(re.findall(r'\w+', langtest))
            spellcheck_de_us(langtest)
            langidresult = langid.classify(whole_text)
            de_mean = (de_errcount / wordcount) * 100
            us_mean = (us_errcount / wordcount) * 100

        # common operations
        statsfh.write ('% DE errors per word: {0:.1f}' . format(de_mean) + '\n')
        statsfh.write ('% US errors per word: {0:.1f}' . format(us_mean) + '\n')
        statsfh.write ('langID: ' + str(langidresult[0]) + '\t{0:.1f}' . format(langidresult[1]) + '\n')

        # get text id from file name (there should not be any error here)
        match = re.search('([0-9]+)', filename)
        textid = match.group(1)

        # store text id, mean DE + US errors, and langID result
        de_values[textid] = de_mean
        us_values[textid] = us_mean
        langid_results[textid] = str(langidresult[0]) + '\t{0:.2f}' . format(langidresult[1])

        statsfh.close()


# display 5 top values
def globalstat(dictname, revbool):
    i = 0
    for item in sorted(dictname, key=dictname.get, reverse=revbool):
        print (item, '{0:.1f}' . format(dictname[item]), sep='\t')
        i += 1
        if i >= args.numval:
            break

print ('Highest DE unknown/words %')
globalstat(de_values, True)
print ('Lowest US unknown/words %')
globalstat(us_values, False)


# global file with global values
with open(args.dir + 'langstat-summary', 'w') as f:
    f.write ('IMDB id' + '\t' + 'DE errors %' + '\t' + 'US errors %' + '\t' + 'langID code' + '\t' + 'confidence' + '\n')
    for key in de_values:
        f.write (str(key) + '\t' + '{0:.2f}' . format(de_values[key]) + '\t' + '{0:.2f}' . format(us_values[key]) + '\t' + langid_results[textid] + '\n')

