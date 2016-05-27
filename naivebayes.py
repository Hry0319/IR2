# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import sqlite3

import numpy as np

from optparse import OptionParser
from Topic import TopicModel

reGenDB = 0

def main():  

    #
    # terminal option parser
    #  
    DataDir             = "../20news/"
    OutPutFile          = "./output.txt"
    Labeled_Data_Size   = ""
    parser = OptionParser()
    parser.add_option("-i", action="store", type="string", dest="DataDir"           , default = DataDir            , help = "")
    parser.add_option("-o", action="store", type="string", dest="OutPutFile"        , default = OutPutFile         , help = "")
    parser.add_option("-n", action="store", type="string", dest="Labeled_Data_Size" , default = Labeled_Data_Size  , help = "")
    (options, args)     = parser.parse_args()
    DataDir             = options.DataDir
    OutPutFile          = options.OutPutFile
    Labeled_Data_Size   = options.Labeled_Data_Size

    TotalWords      = 0
    TopicList       = []
    TrainingDirList = []

    getDirList(DataDir + 'Train/', TrainingDirList)

    # 
    # parse to DB or Select from DB  
    # IF YOU RUN THIS FIRST TIME , BE SURE YOUR SQL TABLE IS GENERATED BEFORE IT
    # 
    if reGenDB :
        TopicModel('test').reset()

        for path in TrainingDirList:
            filelist = []
            getFileList(path, filelist)

            topic    = TopicModel( path[ len(DataDir + 'Train'): ].strip('/') )
            topic.CalProbPerUnigram(filelist)
            TopicList.append(topic)
            # topic.SQL_SUM()
            TotalWords += topic.WordsCount

    else:
        # TotalWords = 164913
        for path in TrainingDirList:
            filelist = []
            getFileList(path, filelist)

            topic    = TopicModel( path[ len(DataDir + 'Train'): ].strip('/') )
            topic.SelectUnigramFromDB()
            TopicList.append(topic)
            # topic.SQL_SUM()
            TotalWords += topic.WordsCount
    # print TotalWords

    #
    #  Cal each Topics' probility     ( sum of these probility is 1.0 )
    #
    for topic in TopicList:
        topic.Probility = float(topic.WordsCount)/TotalWords







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
    