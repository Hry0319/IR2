# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3
# import scipy
import numpy as np

from optparse import OptionParser
from Topic import TopicModel, CommonWords

reGenDB = 1

def main():  

    #
    # terminal option parser
    #  
    DataDir             = "./20news/"
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
        TopicModel.reset()

        for path in TrainingDirList:
            filelist = []
            getFileList(path, filelist)

            topic    = TopicModel( path[ len(DataDir + 'Train'): ].strip('/') )
            topic.CalProbPerUnigram(filelist)
            TopicList.append(topic)
            # topic.SQL_SUM()
            TotalWords += topic.TopicWordsCount

    else:
        for path in TrainingDirList:
            topic = TopicModel( path[ len(DataDir + 'Train'): ].strip('/') )
            topic.SelectUnigramFromDB()
            TopicList.append(topic)
            # topic.SQL_SUM()
            TotalWords += topic.TopicWordsCount
    # print TotalWords

    #
    #  Cal each Topics' Probability     ( sum of these Probability is 1.0 )
    #
    topicFileList = []
    filecounts = 0
    vocabCounts = 0
    for topic in TopicList:
        # topic.TopicProbability = float(topic.TopicWordsCount)/TotalWords
        getFileList(DataDir + 'Train/' + topic.Label , topicFileList)
        filecounts += len(topicFileList)
        topic.TopicProbability = float(len(topicFileList))
        # vocabCounts += len(topic.UnigramCount)

    for topic in TopicList:
        topic.TopicProbability /= float(filecounts)
        # print topic.TopicProbability

    #
    # Classify the test data  
    # There are 9419 files in 20news/test/
    #
    TestDataPath     = DataDir + 'Test/'
    TestDataFileList = []
    AnswerList       = []
    getFileList(TestDataPath, TestDataFileList)

    for path in TestDataFileList:    # test data path list
        AnswerList.append( Classifier(path, TopicList) )


    # print AnswerList
    
    # write answer list to the output.txt    
    WriteOutput(OutPutFile, AnswerList)

    evaluation(AnswerList)


def Classifier(path, TopicList):
    f = open(path)
    Lines = f.readlines()
    f.close()

    TestDataUnigramList = []

    for line in Lines:
        tmpList = TopicModel.getUnigrams(line)
        for Unigram in tmpList:
            if Unigram.isalpha() and Unigram not in CommonWords:
                # print Unigram
                TestDataUnigramList.append(Unigram)
    # print TestDataUnigramList , len(TestDataUnigramList)


    SimilarClass = ""
    tmpL         = 0.0
    Zeta         = 1
    for topic in TopicList:
        Likelihood = 0.0

        for TestDataUni in TestDataUnigramList: 
            Count = topic.UnigramCount.get(TestDataUni)

            if Count != None and Count != 0:
                Likelihood += np.log(Count + Zeta)
                Likelihood -= np.log(topic.TopicWordsCount + topic.VocabCount * Zeta)
            else:                
                Likelihood += np.log(1 + Zeta)
                Likelihood -= np.log(topic.TopicWordsCount + topic.VocabCount * Zeta)

        Likelihood += np.log(topic.TopicProbability)
        Likelihood *= -1
        
        if tmpL == 0.0:
            tmpL = Likelihood
            SimilarClass = topic.Label
        elif Likelihood < tmpL:
            tmpL = Likelihood
            SimilarClass = topic.Label

    return SimilarClass   # return the label name of the file from test




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
    return

def evaluation(output):
    score = 0
    f = open('ans.test.txt')
    ans = f.readlines()
    f.close()
    # f = open('output.txt')
    # output = f.readlines()
    # f.close()
    # for i in xrange(0, len(output)):
    #     if ans[i].strip('\n').split(' ')[1] == output[i]:
    #         score+=1
    for i in xrange(0, len(output)):
        if ans[i] == str(i+1) + ' ' + output[i] + '\n':
            score+=1
    print "\n!!   score : %d   !!\n" % score
    return

def WriteOutput(path, oList):
    f = open(path, 'wb+')    
    f.seek(0)
    count = 0
    for _class in oList:
        f.write(str(count+1) + ' ' + str(oList[count]) + '\n')
        count+=1
        # if count > 50:
            # break
    f.flush()
    f.close()
    return

# main()
if __name__ == '__main__':
    main()
    