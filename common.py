#!/usr/bin/env python
#coding:utf8
import urllib
import urllib2
import httplib
import os
import re
import sys
import time
import logging 
import hmac
import base64
import commands
import mimetypes

from cStringIO import StringIO
#from abc import abstractmethod
from urlparse import urlparse
from datetime import datetime

class FileSystemException(Exception):
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return 'FileSystemException: ' + str(self.msg)

class NotImplementException(Exception):
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return 'NotImplementException: ' + str(self.msg)

###########################################################
# color system
###########################################################

class bcolors:

    BLUE = '\x1b[34m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    RED = '\x1b[31m'
    ENDC = '\x1b[00m'

    def disable(self):
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.RED = ''
        self.ENDC = ''

    @staticmethod
    def bright():  # 31/32/33/34,is dark color, 91/92/93/94 is Bright color
        bcolors.BLUE = '\x1b[94m'
        bcolors.GREEN = '\x1b[92m'
        bcolors.YELLOW = '\x1b[93m'
        bcolors.RED = '\x1b[91m'
        bcolors.ENDC = '\x1b[00m'


def to_red(s):       return  bcolors.RED+ str(s) + bcolors.ENDC
def to_yellow(s):    return  bcolors.YELLOW+ str(s) + bcolors.ENDC
def to_green(s):     return  bcolors.GREEN + str(s) + bcolors.ENDC
def to_blue(s):      return  bcolors.BLUE+ str(s) + bcolors.ENDC

##http://pypi.python.org/pypi/ansicolors/1.0.2#downloads
#from colors import red as to_red
#from colors import green as to_green
#from colors import blue as to_blue
#from colors import yellow as to_yellow

def print_red(s): print to_red(s)
def print_yellow(s): print to_yellow(s)
def print_green(s): print to_green(s)
def print_blue(s): print to_blue(s)


###########################################################
# misc
###########################################################
def shorten(s, l=80):
    if len(s)<=l:
        return s
    return s[:l-3] + '...'

#commands dose not work on windows..
def system(cmd):
    logging.info(cmd)
    r = commands.getoutput(cmd)
    logging.debug(r)
    return r
	
#def system(cmd):
    #logging.info(cmd)
    #from subprocess import Popen, PIPE
    #p = Popen(cmd, shell=True, bufsize = 102400, stdout=PIPE)
    #p.wait()
    #r = p.stdout.read()
    #logging.debug(r)
    #return r

def md5_for_file(f, block_size=2**20):
    f = open(f, 'rb')
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.digest()

def parse_size(input):
    K = 1024
    M = K * K
    G = M * K
    T = G * K
    sizestr = re.search(r'(\d*)', input).group(1)
    size = int(sizestr)
    if input.find("k") > 0 or input.find("K") > 0 :
        size=size*K
    if input.find("m") > 0 or input.find("M") > 0 :
        size=size*M
    if input.find("g") > 0 or input.find("G") > 0 :
        size=size*G
    if input.find("t") > 0 or input.find("T") > 0 :
        size=size*T
    return size

def format_size(input):
    input = int(input)
    K = 1024.
    M = K * K
    G = M * K
    T = G * K
    if input >= T: return '%.2fT' % (input /  T)
    if input >= G: return '%.2fG' % (input /  G)
    if input >= M: return '%.2fM' % (input /  M)
    if input >= K: return '%.2fK' % (input /  K)
    return '%d' % input


def format_time(timestamp):
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    t = datetime.fromtimestamp(float(timestamp))
    return t.strftime(ISOTIMEFORMAT)

'''
set_level 设为
'''
def init_logging(logger, set_level = logging.INFO, 
        console = True,
        log_file_path = None):

    logger.setLevel(logging.DEBUG)
    logger.propagate = False # it's parent will not print log (especially when client use a 'root' logger)
    for h in logger.handlers:
        logger.removeHandler(h)
    if console:
        fh = logging.StreamHandler()
        fh.setLevel(set_level)
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    if log_file_path:
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(set_level)
        formatter = logging.Formatter("%(asctime)-15s %(levelname)s  %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)


