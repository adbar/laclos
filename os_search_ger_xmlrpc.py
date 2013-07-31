#!/usr/bin/python

from __future__ import print_function
import xmlrpclib
import time
import sys

import atexit
import argparse


## TODO:


# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--limit', dest='req_limit', help='maximum number of requests to be made', required=True)
parser.add_argument('-i', '--inputfile', dest='inputfile', help='name of the input file', required=True)
# parser.add_argument('-a', '--all', dest='all', action="store_true", help='process all possible ids')

args = parser.parse_args()

try: 
    req_limit = int(args.req_limit)
except ValueError:
    print ('max. number of requests is not an integer')
    sys.exit()



# time the whole script
start_time = time.time()
req_time = time.time()


## write files
def writefile(filename, listname, append_or_write):
    try:
        outfile = open(filename, append_or_write)
    except IOError:
        sys.exit ('Could not open the output file:', filename)

    for thing in listname:
        outfile.write(thing + '\n')

    outfile.close()


### Exit strategy
# Write all files and logs
@atexit.register
def the_end():
    print ('## END')
    writefile('os_metadata', metadata, 'a')
    writefile('os_seen_ids', seen_ids, 'w')
    writefile('os_all-infos', infos, 'a')
    end_time = time.time() - start_time
    print ('# Total:\t\t\t', total_count)
    print ('# Successful:\t\t\t', successvar)
    print ('# Execution time (secs):\t{0:.2f}' . format(end_time))
    print ('# Secs per request ratio:\t{0:.2f}' . format(end_time/total_count))


## load input list
def load_list(filename):
    temp = list()
    try:
        listfile = open(filename, 'r')
    except IOError:
        sys.exit ('Could not open the file containing the inputlist: ', filename)

    for line in listfile:
        temp.append(line.rstrip())

    listfile.close()
    return temp


imdb_ids = load_list(args.inputfile)

# load seen ids
seen_ids = set()
try:
    seenfile = open('os_seen_ids', 'r')
    for line in seenfile:
        seen_ids.add(line.rstrip())
    seenfile.close()
except IOError:
    print ('no seen file detected')


# vars
total_count = 0
successvar = 0
metadata = list()
infos = list()


## settings
server_url = 'http://api.opensubtitles.org/xml-rpc'
user_agent = 'OS Test User Agent'
language = 'en'
os_server = xmlrpclib.ServerProxy(server_url)

## connect
logininfo = os_server.LogIn('', '', language, user_agent)
print ('login:', logininfo)
token = logininfo['token']
# print (token)


## xmlrpc search function
def search_func(number):
    global metadata, successvar
    params = [({'sublanguageid': 'ger', 'imdbid': number})]
    try:
        search_sub = os_server.SearchSubtitles(token, params)
    # dont't hammer the server if there is a problem
    except xmlrpclib.ProtocolError as err:
        errmsg = "%r" % err
        print (errmsg)
        time.sleep(60)
        return 0
    # print (search_sub)
    if search_sub['data'] is not False:
        successvar += 1
        data = search_sub['data'][0]
        infos.append(str(data))
        metadata.append( str(data['IDMovieImdb'].encode('utf-8')) + '\t' + str(data['IDMovie'].encode('utf-8')) + '\t' + str(data['SubDownloadLink'].encode('utf-8')) + '\t' + str(data['MovieName'].encode('utf-8')) + '\t' + str(data['SubFileName'].encode('utf-8')))
        # 
    else:
        pass

    return 1


## main loop
i = 0
while total_count < req_limit:
    try:
        if imdb_ids[i] not in seen_ids:
            result = search_func(imdb_ids[i])
            if result == 1:
                seen_ids.add(imdb_ids[i])
                total_count += 1
                time.sleep(1)
        i += 1
        if total_count != 0 and total_count % 1000 == 0:
            print (str(total_count) + 'th request', 'sec/request ratio: {0:.2f}' . format((time.time() - req_time)/total_count), sep='\t')
            req_time = time.time()
    except IndexError:
        break


logout = os_server.LogOut(token)
print ('logout:', logout)

