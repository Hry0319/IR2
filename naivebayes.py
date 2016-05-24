# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import numpy as np
from Topic import TopicModel
from optparse import OptionParser
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
#import xml.sax
#import textProc
import sqlite3

#io.DEFAULT_BUFFER_SIZE = 65535
reGenDB = 0

def main():    
    DataDir             = "../20news/"
    OutPutFile          = "./output.txt"
    Labeled_Data_Size   = ""
    TotalWords          = 0

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

#  Cal each Topics' probility     ( sum of these probility is 1.0 )
    for topic in TopicList:
        topic.Probility = float(topic.WordsCount)/TotalWords
        test += topic.Probility







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

# def getSQLiteTable(DB = './Topic.db', TableName='Topic'):
#     self.conn = sqlite3.connect(DB)

#     c = self.conn.cursor()

#     sqlcmd = "SELECT * FROM %s" % (TableName)
#     c.execute(sqlcmd)
#     c.close()
#     self.conn.commit()






# main()
if __name__ == '__main__':
    main()
    