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
    DataDir             = ""
    OutPutFile          = "./output.txt"
    Labeled_Data_Size   = ""

##
## terminal option parser
##
    parser = OptionParser()
    parser.add_option("-i", action="store", dest="string", dest="DataDir"           , default = queryFile          , help = "")
    parser.add_option("-o", action="store", type="string", dest="OutPutFile"        , default = OutPutFile         , help = "")
    parser.add_option("-n", action="store", type="string", dest="Labeled_Data_Size" , default = Labeled_Data_Size  , help = "")
    (options, args) = parser.parse_args()






# main()
if __name__ == '__main__':
    main()
