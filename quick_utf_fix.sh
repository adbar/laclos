#!/usr/bin/bash

## detect charset and correct it if necessary so that all files use UTF-8

for filename in download/temp/*
    do
    encoding=$(file -i $filename | grep -Po 'charset=\K.+?$')
    # echo $filename"\t"$encoding
    destfile="download/test/"$(echo $filename | grep -Po 'IMDBid_.+$')
    # echo $destfile
    # if ! ( echo $encoding | grep -P "^unknown" )
    if [[ ! $encoding =~ "unknown" ]]
    then
        iconv -f $encoding -t UTF-8 < $filename > $destfile #//TRANSLIT
    else
        < $filename sed -e 's/\xDF/ß/g' -e 's/\xE4/ä/g' -e 's/\xF6/ö/g' -e 's/\xFC/ü/g' > $destfile
    fi
    done
