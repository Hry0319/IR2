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
from collections import OrderedDict
from optparse import OptionParser
from Topic import TopicModel, CommonWords, vocab


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
    # if reGenDB :
    #     TopicModel.reset()

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
    # else:
    #     for path in TrainingDirList:
    #         topicnum        += 1
    #         filelist        = []
    #         getFileList(path, filelist)
    #         topic           = TopicModel( path[ len(DataDir + 'Train'): ].strip('/'), topicnum)
    #         topic.SelectUnigramFromDB()
    #         TopicList.append(topic)
    #         TotalWords += topic.TopicWordsCount
    #         TotalFiles += topic.FileCount
    #         VocabSize  += len(topic.UnigramCount)

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


    prevL = 0.0
    nowL  = 0.0
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
    # ~~~~~~~~~~~E & M~~~~~~~~~~~~~
    #
    for step in xrange(0, 2):
        nowL = 0
        '''   E step   '''
        EM_guess = False
        if (step == 0):
            EM_guess = True

        #LogLikelihood
        for topic in TopicList:
            L = topic.cal_LogLikelihood()
            nowL += L


        # Expectations
        for topic in TopicList:
            topic.cal_Expectation(TopicList)   # sum = 1.0

        # predict one time first
        for path in EM_Dataset:
            EM_Classifier(path, TopicList, Data_Topic_dic, EM_guess)

        '''   M step   '''
        for topic in TopicList:
            # topic.FileCount += topic.FileCount;
            topic.TopicProbability = float(topic.FileCount)*topic.Expectation / TotalFiles
            topic.FileCount = 0 # for next time

        TrainingNewModel(TopicList, Data_Topic_dic, TotalWords)

        print 'step : ', step , '      Likelihood sum : ', nowL   , ' growup % : ',(nowL / prevL)


    ##=======================================================================##
    #                            EM ALGORITHM END                             #
    ##=======================================================================##
        if step % 10 != 0:
            continue

        import re
        TestDataPath     = DataDir + 'Test/'
        TestDataFileList = []
        AnswerList       = []
        getFileList(TestDataPath, TestDataFileList)
        TestDataFileList = sorted(TestDataFileList, key=lambda x: (int(re.sub('\D','',x)),x))
        for path in TestDataFileList:    # test data path list
            AnswerList.append( NBClassifier(path, TopicList) )

        # write answer list to the output.txt
        WriteOutput(OutPutFile, AnswerList)
        score = evaluation(AnswerList)


        if nowL < prevL:
            tmpScore = nowL
        if nowL!=0 and prevL!=0:
            if nowL - prevL >0 or (nowL / prevL) < 0.05:
                break


# end ------------------------------------  Main ------------------------------------

def TrainingNewModel(TopicList, Data_Topic_dic, TotalWords):
    for  keyPath  in Data_Topic_dic:
        for topic in TopicList:
            if Data_Topic_dic[keyPath] == topic.TopicNumber:
                topic.EM_FileList.append(keyPath)

    for topic in TopicList:
        topic.EM_UnigramCount = {}
        topic.FileCount = len(topic.EM_FileList)
        topic.EM_CountPerUnigram(topic.EM_FileList)
        topic.TopicProbability = float(topic.TopicWordsCount) / TotalWords
        # topic.dbg_DumpAllAttributeInfo()
    return

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

            if Count != None and Count != 0:
                Likelihood += np.log(Count)
                Likelihood -= np.log(topic.TopicWordsCount)
            else:
                Likelihood += np.log(1 + topic.Zeta)
                Likelihood -= np.log(topic.TopicWordsCount)

        Likelihood += np.log(topic.TopicProbability)
        Likelihood += np.log(topic.Expectation)

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
            Count = topic.EM_UnigramCount.get(TestDataUni)

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
        if ans[i].strip() == str(i+1) + ' ' + output[i].strip():
            score+=1.0
    print "\n!!   score : %f   !!\n" % (score / 9417)
    return score

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

