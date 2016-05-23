# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import numpy as np
from Topic import Topic
from optparse import OptionParser
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
#import xml.sax
#import textProc

#io.DEFAULT_BUFFER_SIZE = 65535


def main():    
    DataDir             = "../20news"
    OutPutFile          = "./output.txt"
    Labeled_Data_Size   = ""

##
## terminal option parser
##
    parser = OptionParser()
    parser.add_option("-i", action="store", type="string", dest="DataDir"           , default = DataDir            , help = "")
    parser.add_option("-o", action="store", type="string", dest="OutPutFile"        , default = OutPutFile         , help = "")
    parser.add_option("-n", action="store", type="string", dest="Labeled_Data_Size" , default = Labeled_Data_Size  , help = "")
    (options, args) = parser.parse_args()



    topic = Topic()













# main()
if __name__ == '__main__':
    main()








