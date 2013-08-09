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
# langid switch
# python 3 ?



# argparse
parser = argparse.ArgumentParser()
parser.add_argument('--langid-lines', dest='langid_lines', action="store_true", help='apply langID line by line (much slower)')
parser.add_argument('-d', '--dir', dest='dir', help='directory where the files are', required=True)
args = parser.parse_args()



# vars
wcounts = list()
de_errs = list()
us_errs = list()
de_stat = list()
de_values = dict()
us_values = dict()
langid_results = dict()


# loop through the existing files
for filename in listdir(args.dir): # test_langid/ korpus/test/

    # sanity check on file name + size
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

            flag = 0
            whole_text += line

            # Check spelling to see if the link text is in English
            langtest = re.sub(r'[^\w\s]', '', line)
            wordcount = len(re.findall(r'\w+', langtest)) # redundant, see enchant.tokenize ?

            if wordcount > 0:

                # DE + US
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


                # langID, if option set
                if args.langid_lines:
                    langidresult = langid.classify(langtest)

                # stats
                statsfh.write (str(wordcount) + '\t{0:.1f}' . format((de_errcount / wordcount) * 100) + '\t')
                statsfh.write ('{0:.1f}' . format((us_errcount / wordcount) * 100) + '\t' + str(flag) + '\t')
                if args.langid_lines:
                    statsfh.write (str(langidresult[0]) + '\t{0:.1f}' . format(langidresult[1]) + '\n')
                else:
                    statsfh.write ('\n')

                wcounts.append(wordcount)
                de_errs.append(de_errcount)
                us_errs.append(us_errcount)

        de_mean = (sum(de_errs) / sum(wcounts) * 100)
        us_mean = (sum(us_errs) / sum(wcounts) * 100)
        langidresult = langid.classify(whole_text)

        statsfh.write ('Mean words per line: {0:.1f}' . format(sum(wcounts) / len(wcounts)) + '\n')
        statsfh.write ('Mean DE errors: {0:.1f}' . format(sum(de_errs) / len(de_errs)) + '\n')
        statsfh.write ('% DE errors per word: {0:.1f}' . format(de_mean) + '\n')
        statsfh.write ('Mean US errors: {0:.1f}' . format(sum(us_errs) / len(us_errs)) + '\n')
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
def globalstat(dictname):
    i = 0
    for item in sorted(dictname, key=dictname.get, reverse=True):
        print (item, '{0:.1f}' . format(dictname[item]), sep='\t')
        i += 1
        if i >= 5:
            break

print ('top DE unknown/words %')
globalstat(de_values)
print ('top US unknown/words %')
globalstat(us_values)


# global file with global values
with open('test_langid/langstat-summary', 'w') as f:
    f.write ('IMDB id' + '\t' + 'DE errors %' + '\t' + 'US errors %' + '\t' + 'langID code' + '\t' + 'confidence' + '\n')
    for key in de_values:
        f.write (str(key) + '\t' + '{0:.2f}' . format(de_values[key]) + '\t' + '{0:.2f}' . format(us_values[key]) + '\t' + langid_results[textid] + '\n')

