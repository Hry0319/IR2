# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3

import numpy as np

from optparse import OptionParser
from Topic import TopicModel, CommonWords

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
    DataDir             = options.DataDir + '/'
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
        TopicModel('ResetDB').reset()

        for path in TrainingDirList:
            filelist = []
            getFileList(path, filelist)

            topic    = TopicModel( path[ len(DataDir + 'Train'): ].strip('/') )
            topic.CalProbPerUnigram(filelist)
            TopicList.append(topic)
            # topic.SQL_SUM()
            TotalWords += topic.WordsCount

    else:
        # TotalWords = 235867
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
    #  Cal each Topics' Probability     ( sum of these Probability is 1.0 )
    #
    for topic in TopicList:
        topic.Probability = float(topic.WordsCount)/TotalWords



    #
    # Classify the test data  
    # There are 9419 files in 20news/test/
    #
    TestDataPath     = DataDir + 'test/'
    TestDataFileList = []
    AnswerList       = []
    getFileList(TestDataPath, TestDataFileList)

    for path in TestDataFileList[:1]:    #test debug
        AnswerList.append( Classifier(path, TopicList) )




def Classifier(path, TopicList):
    f = open(path)
    Lines = f.readlines()
    f.close()

    TestDataUnigramList = []

    for line in Lines:
        trantab = string.maketrans('','')
        delEStr = string.punctuation
        line = line.translate(trantab, delEStr)

        tmpList = line.lower().strip().split(' ')

        for Unigram in tmpList:
            if Unigram.isalpha() and Unigram not in CommonWords:
                # print Unigram
                TestDataUnigramList.append(Unigram)
    # print TestDataUnigramList

    for topic in TopicList[:1]:    #test debug
        for TestDataUni in TestDataUnigramList:  #對每個字去db找data
            """ 2 way to matching Unigram  1, list   2, DB """
            #
            # 1 LIST
            #
            # for Uni, prob in topic.UnigramCount:
            #     if TestDataUni == Uni:
            #         print TestDataUni, prob, "   ", 

            #
            # 2 DB
            #
            Select = DB_Select('WordsCount', 'Topic' ,'Unigram = \''+ TestDataUni+ '\' and TopicName = \''+ topic.Label+'\'')
            for sel, in Select:
                print  sel

            # TopicWordsCount
            # sel
            # NaiveBayes











    return  # return the label name of the file from test



def NaiveBayesProbability(Class, Feature):

    return

def DB_Select(Select ,Table, Where):
    conn = sqlite3.connect('./Topic.db')
    c = conn.cursor()
    sqlcmd = "SELECT %s FROM %s WHERE %s" % (Select, Table ,Where)
    c.execute(sqlcmd)

    data = c.fetchall()
    # for row in data:  # (u'TopicName', u'Unigram', LogProb, WordsCount)
    c.close()

    if data != None:
        return data


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
    