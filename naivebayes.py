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
    DataDir             = "../20news/"
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

    TopicList       = []
    TrainingDirList = []
 
    getDirList(DataDir + 'Train/', TrainingDirList)
    #print TrainingTopicList

#debug clear sql db
    Topic('test').reset()

    for path in TrainingDirList:
    # path = TrainingDirList[0]
    # if path:
        topic = 0
        topic = Topic( path[ len(DataDir + 'Train'): ].strip('/') )
        #topic.reset()

        filelist = []
        getFileList(path, filelist)

        topic.CalProbPerUnigram(filelist)
        TopicList.append(topic)

    # print TopicList[0].Label
    # print TopicList[0].UnigramProb
    # print TopicList[0].WordsCount






def getDirList(path, DirList):
    for item in os.listdir(path):
        if not item.startswith('.') and os.path.isdir(os.path.join(path, item)):
            getDirList(path+item+'/', DirList)
            DirList.append(path+item+'/')

    return


def getFileList(path, FileList):
    for item in os.listdir(path):
        if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
            FileList.append(path + item)


# main()
if __name__ == '__main__':
    main()