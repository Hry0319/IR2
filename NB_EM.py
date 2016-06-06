# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3
# import scipy
import numpy as np
import random

from optparse import OptionParser
from Topic import TopicModel, CommonWords, vocab

reGenDB = 0

# start ------------------------------------  Main ------------------------------------
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
    TotalFiles      = 0
    VocabSize       = 0

    getDirList(DataDir + 'Train/', TrainingDirList)

    #
    # parse to DB or Select from DB
    # IF YOU RUN THIS FIRST TIME , BE SURE YOUR SQL TABLE IS GENERATED BEFORE IT
    #
    topicnum = 0
    if reGenDB :
        TopicModel.reset()


        for path in TrainingDirList:
            topicnum        += 1
            filelist        = []
            getFileList(path, filelist)
            topic           = TopicModel( path[ len(DataDir + 'Train'): ].strip('/'), topicnum)
            topic.FileCount = len(filelist)
            topic.CountPerUnigram(filelist)
            TopicList.append(topic)
            TotalWords += topic.TopicWordsCount
            TotalFiles += topic.FileCount
            VocabSize  += len(topic.UnigramCount)
        # #
        # # add unlabeled data & global vocab
        # #
        # del filelist[:]
        # getFileList(DataDir + 'Unlabel/', filelist)
        # topic           = TopicModel( 'Unlabel' , 0)
        # topic.FileCount = len(filelist)
        # topic.CountPerUnigram(filelist)
        # TopicList.append(topic)
        # TotalWords += topic.TopicWordsCount
        # TotalFiles += topic.FileCount
        # VocabSize  += len(topic.UnigramCount)
        # TopicList.pop()
    else:
        for path in TrainingDirList:
            topicnum        += 1
            filelist        = []
            getFileList(path, filelist)
            topic           = TopicModel( path[ len(DataDir + 'Train'): ].strip('/'), topicnum)
            topic.SelectUnigramFromDB()
            TopicList.append(topic)
            TotalWords += topic.TopicWordsCount
            TotalFiles += topic.FileCount
            VocabSize  += len(topic.UnigramCount)
        # #
        # # add unlabeled data & global vocab
        # #
        # del filelist[:]
        # getFileList(DataDir + 'Unlabel/', filelist)
        # topic           = TopicModel( 'Unlabel' , 0)
        # topic.FileCount = len(filelist)
        # topic.SelectUnigramFromDB()
        # TopicList.append(topic)
        # TotalWords += topic.TopicWordsCount
        # TotalFiles += topic.FileCount
        # VocabSize  += len(topic.UnigramCount)
        # TopicList.pop()
    # print TotalWords, TotalFiles, VocabSize

    #
    #  Cal each Topics' Probability     ( sum of these Probability is 1.0 )
    #
    filecounts = 0
    vocabCounts = 0
    for topic in TopicList:
        # topic.TopicProbability = float(topic.FileCount) / TotalFiles
        # topic.VocabCount       = VocabSize
        topic.TopicProbability = float(topic.TopicWordsCount) / TotalWords
        topic.VocabCount       = VocabSize


    ##=======================================================================##
    #                            EM ALGORITHM START                           #
    ##=======================================================================##
    Data_Topic_dic  = {}
    EM_Dataset      = []
    #
    # Data set     // unlabeled + labeled
    #
    getFileList(DataDir + 'Unlabel/', EM_Dataset)  # not sorted
    for path in TrainingDirList:
        filelist = []
        getFileList(path, filelist)
        EM_Dataset += filelist

    TotalFiles      = len(EM_Dataset)
    Data_Topic_dic  = EM_FileList2Dic(EM_Dataset)



    #
    # E & M
    #
    for step in xrange(0, 1):
        ''' ===== E step ===== '''
        EM_guess = False
        if (step == 0):
            EM_guess = True
        #LogLikelihood
        for topic in TopicList:
            L = topic.cal_LogLikelihood()
        # Expectations
        for topic in TopicList:
            topic.cal_Expectation(TopicList)   # sum = 1.0

        # predict one time first
        for path in EM_Dataset:
            EM_Classifier(path, TopicList, Data_Topic_dic, EM_guess)
        print Data_Topic_dic

        # gen vocab for each topic
        TopicModel.EM_CountPerUnigram_for_vocab(EM_Dataset, vocab)
        for topic in TopicList:
            topic.EM_UnigramCount = vocab.copy()
            # print len(topic.EM_UnigramCount)


        ''' ===== M step ===== '''
        for topic in TopicList:
            # topic.EM_FileCount += topic.FileCount;
            topic.TopicProbability = float(topic.EM_FileCount) / TotalFiles
            topic.EM_FileCount = 0 # for next time


        print 'step : ', step





    ##=======================================================================##
    #                            EM ALGORITHM END                             #
    ##=======================================================================##

    # import re
    # TestDataPath     = DataDir + 'Test/'
    # TestDataFileList = []
    # AnswerList       = []
    # getFileList(TestDataPath, TestDataFileList)
    # TestDataFileList = sorted(TestDataFileList, key=lambda x: (int(re.sub('\D','',x)),x))
    # for path in TestDataFileList:    # test data path list
    #     AnswerList.append( NBClassifier(path, TopicList) )

    # # write answer list to the output.txt
    # WriteOutput(OutPutFile, AnswerList)
    # evaluation(AnswerList)


# end ------------------------------------  Main ------------------------------------



def EM_Classifier(path, TopicList, FileDict, EM_guess = False):
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

    tmpL         = 0.0
    for topic in TopicList:
        Likelihood = 0.0
        for word in TestDataUnigramList:
            if EM_guess == True:
                Count = topic.UnigramCount.get(word)
            else:
                Count = topic.EM_UnigramCount.get(word)

            # print Count

            if Count != None and Count != 0:
                Likelihood += np.log(Count + topic.Zeta)
                Likelihood -= np.log(topic.TopicWordsCount + topic.VocabCount * topic.Zeta)
            else:
                Likelihood += np.log(1 + topic.Zeta)
                Likelihood -= np.log(topic.TopicWordsCount + topic.VocabCount * topic.Zeta)
        # topic.dbg_DumpAllAttributeInfo()

        Likelihood += np.log(topic.TopicProbability)
        Likelihood += np.log(topic.Expectation)
        # Likelihood *= topic.Expectation
        # Likelihood *= -1

        if tmpL == 0.0:
            tmpL = Likelihood
            SimilarClass = topic.Label
        elif Likelihood > tmpL:
            tmpL = Likelihood
            SimilarClass = topic.Label

    for topic in TopicList:
        if SimilarClass == topic.Label:
            FileDict[path] = topic.TopicNumber
            break

    # return SimilarClass   # return the label name of the file from test



def EM_FileList2Dic(EM_Dataset):
    dic = {}
    for path in EM_Dataset:
        dic[path] = 0
    return dic



def NBClassifier(path, TopicList):
    global vocab

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
    Zeta         = 0.5
    for topic in TopicList:
        if topic.Label == 'Unlabel':
            continue
        topic.Zeta = Zeta
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
        # Likelihood *= -1

        if tmpL == 0.0:
            tmpL = Likelihood
            SimilarClass = topic.Label
        elif Likelihood > tmpL:
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
    score = 0.0
    f = open('ans.test.txt')
    ans = f.readlines()
    f.close()

    for i in xrange(0, len(output)):
        if ans[i] == str(i+1) + ' ' + output[i] + '\n':
            score+=1.0
    print "\n!!   score : %f   !!\n" % (score / 9417)
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
