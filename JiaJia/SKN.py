# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3
# import scipy
import numpy as np
from collections import OrderedDict

CommonWords = ['all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should',
     'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did',
     'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 'out', 'what',
     'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about', 'of',
     'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too',
     'themselves', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself',
     'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have',
     'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after', 'most', 'such', 'why', 'a',
     'off', 'i', 'yours', 'so', 'the', 'having', 'once', 'article'
    ]
TopicDict       = {}
Vocab           = {}
path            = "./20news/Train/"
outputPath      = "./JiaJia/"
TopicList       = []
indexV = 1

def getDirList(path, DirList):
    for item in os.listdir(path):
        if not item.startswith('.') and os.path.isdir(os.path.join(path, item)):
            getDirList(path+item+'/', DirList)
            DirList.append(path+item+'/')
    return DirList

def perDirFileList(path):
    FileList = []
    for item in os.listdir(path):
        if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
            FileList.append(item)
    return FileList

def getUnigrams(OneLine):
    trantab = string.maketrans('@.,','   ')
    delEStr = "!\"#$%&'()*+-/:;<=>?[\]^_`{|}~"   #!\"#$%&'()*+-/:;<=>?[\]^_`{|}~
    OneLine = OneLine.translate(trantab, delEStr)
    words   = OneLine.lower().strip().split()
    return words

def parseVocab(path):
    global indexV
    global Vocab
    global CommonWords

    f = open(path)
    Lines = f.readlines()
    f.close()

    UnigramList = []
    for line in Lines:
        UnigramList = getUnigrams(line)  # slice each line with some rule
        for unigram in UnigramList:  # <--------------------
            if unigram.isalpha() and not unigram in CommonWords: # <--------------------
                if not unigram in Vocab:
                    Vocab[unigram] = indexV
                    indexV += 1

def parseToSklnFmt(path):
    global Vocab
    global CommonWords
    # shared_items = set(Vocab.items()) & set(_Vocab.items())
    # print len(shared_items)

    perFileDic = {}

    f = open(path)
    Lines = f.readlines()   # fully get a file's content (each line to a list)
    f.close()

    UnigramList = []

    for line in Lines:
        UnigramList = getUnigrams(line)
        for unigram in UnigramList:  # <--------------------
            if unigram.isalpha() and unigram not in CommonWords: # <--------------------
                if  Vocab[unigram] in perFileDic:
                    perFileDic[Vocab[unigram]] += 1
                else:
                    perFileDic[Vocab[unigram]] = 1

    perFileDic = OrderedDict( sorted(perFileDic.items() ) )

    return perFileDic

##################################################################################################################
TopicList = []
TopicList = getDirList(path, TopicList)
TopicList += ["./20news/Test/"]

for topic in TopicList:
    FileList = perDirFileList(topic)
    for file in FileList:
        parseVocab(topic + file)


# print Vocab
print len(Vocab)




##################################################################################################################

# Training data
index = 0
outPutString = ""
TopicList = []
fo = open(outputPath+"/train.txt", 'wb+')
TopicList = getDirList("./20news/Train/", TopicList)
for topic in TopicList:  # topic is path
    TopicDict[topic] = index
    FileList = perDirFileList(topic)
    for file in FileList:
        fo.write(str(index) + ' ')   # topic number
        perFileDic = parseToSklnFmt(topic + file)
        for key in perFileDic:
            fo.write(' ' + str(key) + ":" + str(perFileDic[key]))
        fo.write('\n')

    index += 1
fo.close()


##################################################################################################################

f = open('ans.test.txt')
anslist = f.readlines()
f.close()
answers = []
for ans in anslist:
    qq = ans.strip().split(' ')
    answers.append(TopicDict['./20news/Train/'+qq[1]+'/'])

##################################################################################################################

# Testing data
fo = open(outputPath+"/test.txt", 'wb+')
FileList = perDirFileList("./20news/Test/")

index = 0
for file in FileList:

    fo.write(str(answers[int(file)-1]) + " ")   # write topic number frome ans.
    DicPerFile = parseToSklnFmt("./20news/Test/" + file)
    for key in DicPerFile:
        fo.write(' ' + str(key) + ":" + str(DicPerFile[key]))
    index += 1
    fo.write('\n')
fo.close()

print FileList[42]
f = open("./20news/Test/" + FileList[42])
read = f.readlines()
f.close
