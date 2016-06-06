 # -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3
import numpy as np
from collections import OrderedDict

vocab = {}

CommonWords = ('all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should',
     'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did',
     'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 'out', 'what',
     'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about', 'of',
     'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too',
     'themselves', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself',
     'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have',
     'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after', 'most', 'such', 'why', 'a',
     'off', 'i', 'yours', 'so', 'the', 'having', 'once', 'article'
    )

"""
CREATE TABLE 'Topic' ('TopicName' CHAR DEFAULT '""', 'Unigram' CHAR DEFAULT '""', 'Probability' DOUBLE DEFAULT '0', 'WordsCount' INTEGER DEFAULT '0')

SQLite table
{
    Topic:
        TopicName       # !!! the diff Topics may have same unigram!!!
        Unigram         # Unigram name
        Probability     # Unigram Probability
        WordsCount      # per unigram
}
"""

class TopicModel:
    Label            = ""    # topic folder dir name
    TopicNumber      = 0     # 0 is XX  , from 1~20
    UnigramCount     = {}    # dictionary : (O) OrderedDict   (X) this dictionary will transform to be a sorted List
    TopicWordsCount  = 0        # totally words count of Topic
    VocabCount       = 0
    FileCount        = 0
    TopicProbability = 0.0
    Zeta             = 0.0

    EM_UnigramCount  = {}
    EM_FileCount     = 0
    EM_Lambda        = 0.0
    LogLikelihood    = 0.0
    Expectation      = 0.0

    def cal_Expectation(self, TopicList):
        numerator   = 0.0
        denominator = 0.0

        numerator   = self.LogLikelihood + np.log(self.TopicProbability)
        for topic in TopicList:
            denominator += topic.LogLikelihood + np.log(topic.TopicProbability)

        self.Expectation = numerator / denominator  # divide

        return self.Expectation

    def cal_LogLikelihood(self):
        LogL = 0.0
        if len(self.EM_UnigramCount) != 0:
            for key in self.EM_UnigramCount:
                LogL += np.log(self.EM_UnigramCount[key] + self.Zeta)
                LogL -= np.log(self.TopicWordsCount + self.VocabCount * self.Zeta)
            # LogL += np.log(self.TopicProbability)
            self.LogLikelihood = LogL
            return LogL
        else:
            for key in self.UnigramCount:
                LogL += np.log(self.UnigramCount[key] + self.Zeta)
                LogL -= np.log(self.TopicWordsCount + self.VocabCount * self.Zeta)
            # LogL += np.log(self.TopicProbability)
            self.LogLikelihood = LogL
            return LogL

    def EM_CountPerUnigram(self, FileList):
        """
        FileList from only one Topic Folder within the file path
        """
        for file in FileList:
            f = open(file)
            Lines = f.readlines()
            f.close()

            for line in Lines:
                wordslist   = self.getUnigrams(line)
                for Unigram in wordslist:
                    if Unigram.isalpha() and not Unigram in CommonWords:
                        self.TopicWordsCount+= 1
                        if not Unigram in self.EM_UnigramCount:
                            self.EM_UnigramCount[Unigram] = 1.0
                        else:
                            self.EM_UnigramCount[Unigram] += 1.0

    def SelectUnigramFromDB(self):
        """
        Be sure your DB is not empty
        """
        self.TopicWordsCount = 0
        c = self.conn.cursor()
        sqlcmd = "SELECT * FROM Topic WHERE TopicName=\'%s\'" % (self.Label)
        c.execute(sqlcmd)
        data = c.fetchall()
        for row in data:
            self.UnigramCount[str(row[1])] = row[3]
            self.TopicWordsCount += int(row[3])
            #
            # set global vocab
            #
            # TopicModel.setVocab(str(row[1]), int(row[3]))
        c.close()

    def CountPerUnigram(self, FileList):
        """
        FileList from only one Topic Folder within the file path
        """
        for file in FileList:
            f = open(file)
            Lines = f.readlines()
            f.close()

            for line in Lines:
                wordslist   = self.getUnigrams(line)
                for Unigram in wordslist:
                    if Unigram.isalpha() and not Unigram in CommonWords:
                        self.TopicWordsCount+= 1
                        if not Unigram in self.UnigramCount:
                            self.UnigramCount[Unigram] = 1.0
                        else:
                            self.UnigramCount[Unigram] += 1.0
                        #
                        # set global vocab
                        #
                        # TopicModel.setVocab(Unigram, 1.0)

        c = self.conn.cursor()
        for unigram in self.UnigramCount:
            prob = 0
            sqlcmd = "INSERT INTO Topic VALUES(%s, %s, %f, %d)" % ('\''+self.Label+'\'', '\''+unigram+'\'', prob, self.UnigramCount[unigram])
            c.execute(sqlcmd)
        c.close()
        self.conn.commit()

    def SQL_SUM(self):
        # get TopicWordsCountfrom DB
        c = self.conn.cursor()
        sqlcmd2 = "SELECT SUM(WordsCount) FROM Topic where TopicName='%s'" % (self.Label)
        c.execute(sqlcmd2)
        print self.Label, int(c.fetchone()[0]), self.TopicWordsCount



    @classmethod
    def reset(self):
        conn = sqlite3.connect('./Topic.db')
        c = conn.cursor()
        try:
            c.execute('delete from Topic')
        finally:
            c.close()
            conn.commit()

    @staticmethod
    def getUnigrams(OneLine):
        trantab = string.maketrans('@.,','   ')  #@.,
        delEStr = "!\"#$%&'()*+-/:;<=>?[\]^_`{|}~"
        OneLine = OneLine.translate(trantab, delEStr)
        words   = OneLine.lower().strip().split()
        return words

    # @staticmethod
    # def setVocab(key, value):
    #     global vocab
    #     if not key in vocab:
    #         vocab[key] = value
    #     else:
    #         vocab[key] += value
    #     return

    @staticmethod
    def EM_CountPerUnigram_for_vocab(FileList, vocab):
        """
        FileList from only one Topic Folder within the file path
        """
        TopicWordsCount = 0
        for file in FileList:
            f = open(file)
            Lines = f.readlines()
            f.close()

            for line in Lines:
                wordslist   = TopicModel.getUnigrams(line)
                for Unigram in wordslist:
                    if Unigram.isalpha() and not Unigram in CommonWords:
                        TopicWordsCount+= 1
                        if not Unigram in vocab:
                            vocab[Unigram] = 1.0
                        else:
                            vocab[Unigram] += 1.0
        return TopicWordsCount

    def __init__(self, label, TopicNum):
        self.conn             = sqlite3.connect('./Topic.db')
        self.Label            = label
        self.TopicNumber      = TopicNum
        self.TopicWordsCount  = 0
        self.VocabCount       = 0
        self.FileCount        = 0
        self.TopicProbability = 0.0
        self.Zeta             = 0.5
        self.UnigramCount     = {}
        self.EM_UnigramCount  = {}
        self.EM_FileCount     = 0
        self.EM_Lambda        = 0.0
        self.LogLikelihood    = 0.0
        self.Expectation      = 0.0

    def dbg_DumpAllAttributeInfo(self):
        print "Label                   :  ", self.Label
        print "TopicNumber             :  ", self.TopicNumber
        print "TopicWordsCount         :  ", self.TopicWordsCount
        print "VocabCount              :  ", self.VocabCount
        print "FileCount               :  ", self.FileCount
        print "TopicProbability        :  ", self.TopicProbability
        print "Zeta                    :  ", self.Zeta
        print "UnigramCount      size  :  ", len(self.UnigramCount)
        print "EM_UnigramCount   size  :  ", len(self.EM_UnigramCount)
        print "EM_FileCount            :  ", self.EM_FileCount
        print "EM_Lambda               :  ", self.EM_Lambda
        print "LogLikelihood           :  ", self.LogLikelihood
        print "Expectation             :  ", self.Expectation
