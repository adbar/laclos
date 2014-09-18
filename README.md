Language-classified OpenSubtitles
=================================

Copyright (C) Adrien Barbaresi, BBAW (Berlin-Brandenburg Academy of Sciences), 2013-2014.
This is free software, licensed under the GNU Lesser General Public License (https://www.gnu.org/licenses/lgpl.html)


Download the subtitles
----------------------

### Search the dumps for new IDs

    bash process_dumps.sh

### Download the metadata corresponding to the new IDs

One has to request an API key on opensubtitles.org in order to access the XMLRPC interface.

Sleep time and number of subtitles metadata retrieved is left to the discretion of the user, the following values are valid examples:

    python os_search_ger_xmlrpc.py -i new_ids --sleep 1 -l 2000

### remove session IDs

Not strictly necessary.

    sed -e "s/\/src-api\/[a-z0-9-]*//g" -e "s/\/sid\-[a-z0-9]*//g" os_metadata > os_metadata_cleaned
    cp os_metadata_cleaned korpus/metadata

### wget the files

Download on a daily basis is required in order to download a substantial number of subtitles, since limitations are enforced by `opensubtitles.org`. The following script is an example of how files may be downloaded locally:

    bash daily-wget.sh

In order to be more efficient, the same approach should be used from multiple IPs. The script named `dl-list-generator.py` generates a number of sets of equal length that are meant to be sent to remote machines.


Process the documents
---------------------

### launch processing chain

The shell script `korpus-workflow.sh` is designed to articulate the processing chain.

The UNIX utility `file` is used to guess the encoding, and then `iconv` is used to convert the files. It does not always work perfectly, though usual problems with ISO-8859-1 and Unicode are addressed.

The `subfiles-cleaner_enbloc.py` script is the most important part of the processing chain, since it extracts and formats the content. It also removes unwanted text using specially crafted filters for German. It contains a sentence splitter which can be deactivated. Blacklisting of subtitles IDs is possible. The script outputs text or XML files.

### start XML export

This `xml-export.py` script performs a conversion to a valid XML TEI format and adds relevant metadata collected on the XMLRPC interface. As such, it requires a file named `os-metadata`.

    python xml-export.py --inputdir DIRECTORY --outputdir DIRECTORY


Remove unwanted files
---------------------

### Language test

The language-identification script is to be used with two different systems:
- [The Enchant library](http://abisource.com/projects/enchant/) and its Python interface (package python-enchant on Debian/Ubuntu)
- [The langid.py language identification system](https://github.com/saffsd/langid.py)

The `language_check.py` script takes a directory as input and outputs the ID-numbers of the texts containing respectively the most and the less unknown words or lines. The texts are tested for German as well as English (US) as a concurrent language, which is useful to detect irregularities.

    python language_check.py -d DIRECTORY

Possible arguments:
- --numval (number of best and worst values to show at the end)
- --line-by-line line-based language identification, much slower

### Generate blacklist

    python badlistgen.py --summary FILE --output FILE

Expects two files: a summary provided by the language identification software just above and a name for the output file.


Quality assessment
------------------

N-gram extraction, for example this software: http://homepages.inf.ed.ac.uk/lzhang10/ngram.html


Remarks
-------

The scripts usually feature an integrated help prompt, just enter

    python scriptname.py -h

