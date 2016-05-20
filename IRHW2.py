# -*- coding: utf-8 -*-
#from __future__ import print_function  # Py 2.6+; In Py 3k not needed
import os
import io
import sys
import gc
import numpy as np
from optparse import OptionParser
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
#import xml.sax
#import textProc

#io.DEFAULT_BUFFER_SIZE = 65535


def main():    
    queryFile  = ""
    pathNTCIR  = ""
    pathModel  = ""
    rankedList = ""

##
## terminal option parser
##
    parser = OptionParser()
    parser.add_option("-r", action="store_true", dest="relevanceFeedback", help = "turn on relevance feedback")
    parser.add_option("-i", action="store", type="string", dest="queryFile" , default = queryFile  , help = "input query file")
    parser.add_option("-o", action="store", type="string", dest="NTCIR"     , default = pathNTCIR  , help = "dir of NTCIR docs")
    parser.add_option("-m", action="store", type="string", dest="Model"     , default = pathModel  , help = "input model dir")
    parser.add_option("-d", action="store", type="string", dest="rankedlist", default = rankedList , help = "output ranked list file")
    (options, args) = parser.parse_args()







# main()
if __name__ == '__main__':
    main()
