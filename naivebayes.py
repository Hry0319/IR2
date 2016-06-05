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
from Topic import TopicModel, CommonWords

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
            # topic.SQL_SUM()
            TotalWords += topic.TopicWordsCount
            TotalFiles += topic.FileCount
            VocabSize  += len(topic.UnigramCount)

    else:
        for path in TrainingDirList:
            filelist        = []
            getFileList(path, filelist)
            topic           = TopicModel( path[ len(DataDir + 'Train'): ].strip('/') )
            topic.FileCount = len(filelist)
            topic.SelectUnigramFromDB()
            TopicList.append(topic)
            # topic.SQL_SUM()
            TotalWords += topic.TopicWordsCount
            TotalFiles += topic.FileCount
            VocabSize  += len(topic.UnigramCount)
    # print TotalWords, TotalFiles, VocabSize

    #
    #  Cal each Topics' Probability     ( sum of these Probability is 1.0 )
    #
    filecounts = 0
    vocabCounts = 0
    for topic in TopicList:
        topic.TopicProbability = float(topic.FileCount) / TotalFiles
        topic.VocabCount       = VocabSize


    #
    # Classify the test data  
    # There are 9419 files in 20news/test/
    #
    import re
    TestDataPath     = DataDir + 'Test/'
    TestDataFileList = []
    AnswerList       = []
    getFileList(TestDataPath, TestDataFileList)
    TestDataFileList = sorted(TestDataFileList, key=lambda x: (int(re.sub('\D','',x)),x))
    for path in TestDataFileList:    # test data path list
        AnswerList.append( NBClassifier(path, TopicList) )



    
    # first theta
    log_Ls = []
    sum_L = LambdaLogLikelihoodRange(TopicList, log_Ls)
    # print log_Ls, sum_L

    EM_Dataset = []
    getFileList(DataDir + 'Unlabel/', EM_Dataset)  # not sorted
    for path in TrainingDirList:
        filelist = []
        getFileList(path, filelist)
        EM_Dataset += filelist

    TotalFiles = len(EM_Dataset)
    # print TotalFiles 
    # os._exit(0) 

    # EM ALGORITHM 
    for step in xrange(1, 5):
        sum_tmp = 0.0
        ''' E-step M-step '''
        for unalbelFile in EM_Dataset:
            EM_cal_Lc(unalbelFile, TopicList)

        # i = 0
        for topic in TopicList:
            # topic.EM_FileCount += topic.FileCount;
            topic.TopicProbability = float(topic.EM_FileCount) / TotalFiles
            topic.EM_FileCount = 0 # for next time
            sum_tmp += topic.TopicProbability
            L = topic.cal_LogLikelihood()
            L += np.log(topic.TopicProbability)
        #     print i , topic.TopicProbability , L
        #     i += 1
        # print '--- ' + str(sum_tmp) + '--- \n'






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

def EM_cal_Lc(path, TopicList):  #look like funtcion Classifier
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

    SimilarClass = ""
    tmpL         = 0.0
    Zeta         = 0.5
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
        # Likelihood *= -1
        
        if tmpL == 0.0:
            tmpL = Likelihood
            SimilarClass = topic.Label
        elif Likelihood > tmpL:
            tmpL = Likelihood
            SimilarClass = topic.Label

    #
    # update topicProb
    #
    for topic in TopicList:
        if SimilarClass == topic.Label:
            topic.EM_FileCount += 1


    # return SimilarClass   # return the label name of the file from test

def LambdaLogLikelihoodRange(Topics, outLikelihoodList):
    del outLikelihoodList[:]
    Sum = 0
    for topic in Topics:
        L = topic.cal_LogLikelihood()
        if L != None:
            Sum += L
            outLikelihoodList.append(L)
            #?? Accumulation
    return Sum

def NBClassifier(path, TopicList):
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
    