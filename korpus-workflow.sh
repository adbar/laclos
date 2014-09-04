#!/bin/bash

###	This script is part of LACLOS (https://github.com/adbar/laclos).
###	Copyright (C) Adrien Barbaresi, 2013.

## TODO:
# iconv: binary exception
# iconv: ungültige Eingabe-Sequenz
# stripping size error


# Create a temporary file
tempfile() {
    tempprefix=$(basename "$0")
    mktemp /tmp/${tempprefix}.XXXXXX
}
TMP=$(tempfile)
trap 'rm -f $TMP' EXIT


inputdir="korpus/temp/*"
outputdir="korpus/utf8/"


## detect charset and correct it if necessary so that all files use UTF-8

for filename in $inputdir
    do
    encoding=$(file -i $filename | grep -Po 'charset=\K.+?$')
    # echo $filename"\t"$encoding
    destfile=$outputdir$(echo $filename | grep -Po 'IMDBid_.+$')"_utf-8"
    # echo $destfile
    # if ! ( echo $encoding | grep -P "^unknown" )
    if [[ ! $encoding =~ "unknown" ]]
    then
        iconv -f $encoding -t UTF-8//TRANSLIT < $filename > $destfile #//TRANSLIT
        if [[ ! $? == 0 ]]
        then
            echo "Problem with iconv (1), file: "$filename
            iconv -f ISO-8859-1 -t UTF-8//TRANSLIT < $filename > $destfile #//TRANSLIT
            if [[ ! $? == 0 ]]
            then
                echo "Problem with iconv (2), file: "$filename
                # skip file ?
                
            fi
        fi
    else
        iconv -f ISO-8859-1 -t UTF-8//TRANSLIT < $filename > $destfile #//TRANSLIT
        if [[ ! $? == 0 ]]
        then
            echo "Problem with iconv (2), file: "$filename
            # skip file ?
        fi
    fi
    < $destfile sed -e "s/\xc3\x9F/ß/g" -e "s/\xc3\xa4/ä/g" -e "s/\xc3\xb6/ö/g" -e "s/\xc3\xbc/ü/g" -e "s/\xc3\x84/Ä/g" -e "s/\xc3\x96/Ö/g" -e "s/\xc3\x9c/Ü/g" -e "s/\xc2\x86//g" -e "s/\x01//g" > $TMP
    mv $TMP $destfile
    done


# python subfiles-cleaner_enbloc.py --split-sentences --input-dir $outputdir --output-dir korpus/test/ --blacklist subfiles-blacklist
python subfiles-cleaner_enbloc.py --input-dir $outputdir --output-dir korpus/test/ --blacklist subfiles-blacklist --xml-output

cat korpus/test/* > bigOSdump


sort bigOSdump | uniq -c | sort -nrk 1 | head -10000 > 1sgrams

# http://homepages.inf.ed.ac.uk/lzhang10/ngram.html
korpus/ngram-extraction/text2ngram -o corpus bigOSdump
korpus/ngram-extraction/extractngram -n1 -f100 -i corpus | sort -nrk2 > 1ntest
korpus/ngram-extraction/extractngram -n2 -f50 -i corpus | sort -nrk3 > 2ntest
korpus/ngram-extraction/extractngram -n3 -f20 -i corpus | sort -nrk4 > 3ntest
korpus/ngram-extraction/extractngram -n4 -f10 -i corpus | sort -nrk5 > 4ntest
korpus/ngram-extraction/extractngram -n5 -f5 -i corpus | sort -nrk6 > 5ntest


rm corpus.*
rm bigOSdump


python language_check.py -d korpus/test/ &> language-check.log


