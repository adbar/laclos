#!/bin/bash

###	This script is part of LACLOS (https://github.com/adbar/laclos).
###	Copyright (C) Adrien Barbaresi, 2013.
###	This is free software, licensed under the GNU Lesser General Public License (https://www.gnu.org/licenses/lgpl.html)

### LOCAL

cut -f1 set_1 > imdbids
cut -f2 set_1 > gzlist

idlist=( `cat "imdbids" `)
gzlist=( `cat "gzlist" `)

i=0
for id in "${idlist[@]}"; do
    echo -e $i"\t"$id"\t"${gzlist[i]}

    downloadname=$id".gz"
    srtname="IMDBid_"$id
    if [ -f temp/$downloadname ]; then
        downloadname=$id"_b.gz"
        srtname="IMDBid_"$id"_b"
        if [ -f temp/$downloadname ]; then
            downloadname=$id"_c.gz"
            srtname="IMDBid_"$id"_c"
            if [ -f temp/$downloadname ]; then
                echo "Problem by id "$id": too much files for same id" 
            fi
        fi
    fi
    wget -a wget.log -nv ${gzlist[i]} --limit-rate=100k -O temp/$downloadname
    gunzip -c temp/$downloadname > temp/$srtname

    sleep 1
    ((i++))
done

rm imdbids gzlist



