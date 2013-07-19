#!/bin/bash


# TODO:
# check if file ids are already there


cut -f1 things_500 > imdbids
cut -f3 things_500 > gzlist

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

    sleep 2
    ((i++))
done



