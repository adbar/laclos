#!/usr/bin/python

from __future__ import print_function
import xmlrpclib
import time
import sys


## load lists
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
ids = load_list('OS_de_osid')
# imdb_count = 0
# id_count = 0
total_count = 0
successvar = 0
things = list()


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
        # print (data)
        things.append( str(data['IDMovieImdb']) + '\t' + str(data['IDMovie']) + '\t' + str(data['SubDownloadLink']) + '\t' + str(data['SubFileName']) + '\n' )
    else:
        pass

    return


for i in range(0, 5):
    search_func(imdb_ids[i])
    # search_func(ids[i])
    total_count += 1
    time.sleep(1)


logout = os_server.LogOut(token)
print ('logout:', logout)

print ('Total:', total_count)
print ('Successful:', successvar)
# print ('IMDB:', imdb_count)
# print ('OS:', id_count)


try:
    outfile = open('test_links', 'w')
except IOError:
    sys.exit ('Could not open the output file: test_links')

for thing in things:
    outfile.write(thing)

outfile.close()

#temp = json.loads(str(logininfo))
#print (temp['token'])



# match = re.search(r"'token': '([0-9a-z]+?)'", str(logininfo))
#if match:
#    token = match.group(1)
#    print (token)


