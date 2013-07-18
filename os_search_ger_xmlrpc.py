#!/usr/bin/python

from __future__ import print_function
import xmlrpclib
import time
import sys


## TODO:
# argparse: filenames, reqlimit, etc.


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


req_limit = 1000
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

def search_func(number):
    global things, successvar
    params = [({'sublanguageid': 'ger', 'imdbid': number})]
    search_sub = os_server.SearchSubtitles(token, params)
    # print (search_sub)
    if search_sub['data'] is not False:
        successvar += 1
        data = search_sub['data'][0]
        infos.append(str(data))
        things.append( str(data['IDMovieImdb']) + '\t' + str(data['IDMovie']) + '\t' + str(data['SubDownloadLink']) + '\t' + str(data['MovieName']) + '\t' + str(data['SubFileName']))
    else:
        pass

    return

i = 0
while total_count < req_limit:
    if imdb_ids[i] not in seen_ids:
        search_func(imdb_ids[i])
        seen_ids.add(imdb_ids[i])
        total_count += 1
        time.sleep(1)
    i += 1


logout = os_server.LogOut(token)
print ('logout:', logout)

print ('Total:', total_count)
print ('Successful:', successvar)
# print ('IMDB:', imdb_count)
# print ('OS:', id_count)


def writefile(filename, listname, append_or_write):
    try:
        outfile = open(filename, append_or_write)
    except IOError:
        sys.exit ('Could not open the output file:', filename)

    for thing in listname:
        outfile.write(thing + '\n')

    outfile.close()

writefile('test_things', things, 'a')
writefile('seen_ids', seen_ids, 'w')
writefile('test_infos', infos, 'a')





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
