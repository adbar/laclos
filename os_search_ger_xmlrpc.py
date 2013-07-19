#!/usr/bin/python

from __future__ import print_function
import xmlrpclib
import time
import sys

import atexit
import argparse


## TODO:
# argparse: filenames, time limit


# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--limit', dest='req_limit', help='maximum number of requests to be made', required=True)
#parser.add_argument('-i', '--inputfile', dest='inputfile', help='name of the input file', required=True)
#parser.add_argument('-p', '--plot', dest='plot', action="store_true", help='display results as a plot') # does not work in python3
args = parser.parse_args()

try: 
    req_limit = int(args.req_limit)
except ValueError:
    print ('max. number of requests is not an integer')
    sys.exit()



# time the whole script
start_time = time.time()


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
    writefile('test_things', things, 'a')
    writefile('seen_ids', seen_ids, 'w')
    writefile('test_infos', infos, 'a')
    end_time = time.time() - start_time
    print ('Execution time (secs): {0:.2f}' . format(end_time))
    print ('Sec per request ratio: {0:.2f}' . format(end_time/total_count))


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

imdb_ids = load_list('OS_de_IMDBid')

# load seen ids
seen_ids = set()
try:
    seenfile = open('seen_ids', 'r')
    for line in seenfile:
        seen_ids.add(line.rstrip())
    seenfile.close()
except IOError:
    print ('no seen file detected')


# vars
total_count = 0
successvar = 0
things = list()
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
    global things, successvar
    params = [({'sublanguageid': 'ger', 'imdbid': number})]
    try:
        search_sub = os_server.SearchSubtitles(token, params)
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
        things.append( str(data['IDMovieImdb'].encode('utf-8')) + '\t' + str(data['IDMovie'].encode('utf-8')) + '\t' + str(data['SubDownloadLink'].encode('utf-8')) + '\t' + str(data['MovieName'].encode('utf-8')) + '\t' + str(data['SubFileName'].encode('utf-8')))
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
        if total_count != 0 and total_count % 500 == 0:
            print (str(total_count) + 'th request', 'sec/request ratio: {0:.2f}' . format((time.time() - start_time)/total_count), sep='\t')
    except IndexError:
        break


logout = os_server.LogOut(token)
print ('logout:', logout)

print ('Total:', total_count)
print ('Successful:', successvar)
# print ('IMDB:', imdb_count)
# print ('OS:', id_count)





### TRASH

#temp = json.loads(str(logininfo))
#print (temp['token'])


# match = re.search(r"'token': '([0-9a-z]+?)'", str(logininfo))
#if match:
#    token = match.group(1)
#    print (token)


# ids = load_list('OS_de_osid')
# imdb_count = 0
# id_count = 0
