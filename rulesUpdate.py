import urllib, urllib2, tarfile
import os
from os import walk
from os import system

def update():
    URL = 'http://rules.emergingthreats.net/open/snort-2.9.0/emerging.rules.tar.gz'
    urllib.urlretrieve(URL, 'emerging.rules.tar.gz')
    tar = tarfile.open('emerging.rules.tar.gz', 'r')
    for file in tar.getmembers():
        tar.extract(file)
        
    os.system("rsync -ar rules/ /usr/local/snort/rules")
    os.system("rm emerging.rules.tar.gz")
    os.system("rm -rf rules")
        
