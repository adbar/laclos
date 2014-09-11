#!/bin/bash

###	This script is part of LACLOS (https://github.com/adbar/laclos).
###	Copyright (C) Adrien Barbaresi, 2013.
###	This is free software, licensed under the GNU Lesser General Public License (https://www.gnu.org/licenses/lgpl.html)


# get the dumps
wget http://www.opensubtitles.org/addons/export_imdb2.php -O dump_ISO-2
wget http://www.opensubtitles.org/addons/export_imdb.php -O dump_ISO-3
wget http://www.opensubtitles.org/addons/export_movie.php -O dump_movies


# process
python de_extractor.py


# archive
tar cjf dumps-backup.tar.bz2 dump_*
rm dump_*


