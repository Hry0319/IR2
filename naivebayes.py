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

# ------------------------------------  Main ------------------------------------ start
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
    if reGenDB :
        TopicModel.reset()


        for path in TrainingDirList:
            filelist        = []
            getFileList(path, filelist)
            topic           = TopicModel( path[ len(DataDir + 'Train'): ].strip('/') )
            topic.FileCount = len(filelist)
            topic.CalProbPerUnigram(filelist)
            TopicList.append(topic)
            TotalWords += topic.TopicWordsCount
            TotalFiles += topic.FileCount
            VocabSize  += len(topic.UnigramCount)
        #
        # add unlabeled data & global vocab
        #
        del filelist[:]
        getFileList(DataDir + 'Unlabel/', filelist)
        topic           = TopicModel( 'Unlabel' )
        topic.FileCount = len(filelist)
        topic.CalProbPerUnigram(filelist)
        TopicList.append(topic)
        TotalWords += topic.TopicWordsCount
        TotalFiles += topic.FileCount
        VocabSize  += len(topic.UnigramCount)
        TopicList.pop()
    else:
        for path in TrainingDirList:
            filelist        = []
            getFileList(path, filelist)
            topic           = TopicModel( path[ len(DataDir + 'Train'): ].strip('/') )
            topic.FileCount = len(filelist)
            topic.SelectUnigramFromDB()
            TopicList.append(topic)
            TotalWords += topic.TopicWordsCount
            TotalFiles += topic.FileCount
            VocabSize  += len(topic.UnigramCount)
        #
        # add unlabeled data & global vocab
        #
        del filelist[:]
        getFileList(DataDir + 'Unlabel/', filelist)
        topic           = TopicModel( 'Unlabel' )
        topic.FileCount = len(filelist)
        topic.SelectUnigramFromDB()
        TopicList.append(topic)
        TotalWords += topic.TopicWordsCount
        TotalFiles += topic.FileCount
        VocabSize  += len(topic.UnigramCount)
        TopicList.pop()
    # print TotalWords, TotalFiles, VocabSize
    print len(vocab)  #79204


    #
    #  Cal each Topics' Probability     ( sum of these Probability is 1.0 )
    #
    filecounts = 0
    vocabCounts = 0
    for topic in TopicList:
        topic.TopicProbability = float(topic.FileCount) / TotalFiles
        topic.VocabCount       = VocabSize
        # topic.TopicProbability = float(topic.TopicWordsCount) / TotalWords
        # topic.VocabCount       = VocabSize



    ##=======================================================================##
    #                            EM ALGORITHM START                           #
    ##=======================================================================##

    #
    # Data set
    #
    EM_Dataset = []
    getFileList(DataDir + 'Unlabel/', EM_Dataset)  # not sorted
    for path in TrainingDirList:
        filelist = []
        getFileList(path, filelist)
        EM_Dataset += filelist
    TotalFiles = len(EM_Dataset)


    for step in xrange(0, 5)
        '''E step'''
        # Expectations
        for topic in TopicList:
            L = topic.cal_LogLikelihood()
            # print topic.LogLikelihood
        for topic in TopicList:
            topic.cal_Expectation(TopicList)   # sum = 1.0 if use divide
            

    

        '''M step'''
        topic.EM_Lambda = topic.Expectation

        theta = 0.0

        for doc in EM_Dataset:
            


    # Lambda = 0.0
    # for topic in TopicList:
    #     for doc in EM_Dataset:
    #         EM_cal_Lambda(doc, TopicList)
    #     print topic.EM_Lambda


    


    ##=======================================================================##
    #                            EM ALGORITHM END                             #
    ##=======================================================================##



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
    evaluation(AnswerList)
# ------------------------------------  Main ------------------------------------ end

def EM_cal_Theta(path, TopicList):  #look like funtcion Classifier
    global vocab

    f = open(path)
    Lines = f.readlines()
    f.close()
    EM_UnigramList = []
    for line in Lines:
        tmpList = TopicModel.getUnigrams(line)
        for Unigram in tmpList:
            if Unigram.isalpha() and Unigram not in CommonWords:
                # print Unigram
                EM_UnigramList.append(Unigram)
    Xij     = len(EM_UnigramList)
    Lambda  = 0.0
    for topic in TopicList:
        if topic.Label == 'Unlabel':
            continue
        Lambda = (topic.Expectation * Xij) / (topic.Expectation * topic.TopicWordsCount)
        # print Lambda
        topic.EM_Lambda += Lambda

def EM_cal_Lambda(path, TopicList):  #look like funtcion Classifier
    global vocab

    f = open(path)
    Lines = f.readlines()
    f.close()
    EM_UnigramList = []
    for line in Lines:
        tmpList = TopicModel.getUnigrams(line)
        for Unigram in tmpList:
            if Unigram.isalpha() and Unigram not in CommonWords:
                # print Unigram
                EM_UnigramList.append(Unigram)
    Xij     = len(EM_UnigramList)
    Lambda  = 0.0
    for topic in TopicList:
        if topic.Label == 'Unlabel':
            continue
        Lambda = (topic.Expectation * Xij) / (topic.Expectation * topic.TopicWordsCount)
        # print Lambda
        topic.EM_Lambda += Lambda





# def LambdaLogLikelihoodRange(Topics, outLikelihoodList):
#     del outLikelihoodList[:]
#     Sum = 0
#     for topic in Topics:
#         L = topic.cal_LogLikelihood()
#         if L != None:
#             Sum += L
#             outLikelihoodList.append(L)
#             #?? Accumulation
#     return Sum

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
    Zeta         = 0.2
    for topic in TopicList:
        if topic.Label == 'Unlabel':
            continue
        topic.Zeta = Zeta
        Likelihood = 0.0

        for TestDataUni in TestDataUnigramList: 
            Count = topic.UnigramCount.get(TestDataUni)
            inVocab = vocab.get(TestDataUni)

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


# class enumTopic:
#     alt.atheism,
#     comp.graphics,
#     comp.os.ms-windows.misc,
#     comp.sys.ibm.pc.hardware,
#     comp.sys.mac.hardware
#     comp.windows.x
#     misc.forsale
#     rec.autos
#     rec.motorcycles
#     rec.sport.baseball
#     rec.sport.hockey
#     sci.crypt
#     sci.electronics
#     sci.med
#     sci.space
#     soc.religion.christian
#     talk.politics.guns
#     talk.politics.mideast
#     talk.politics.misc
#     talk.religion.misc

# main()
if __name__ == '__main__':
    main()
    