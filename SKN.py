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

Vocab 	   		= {}
path       		= "./20news/Train/"
outputPath 		= "./JiaJia/"
TopicList  		= []
indexV = 0

# class Topic:
# 	Label 			= ""
# 	TopicWordsCount = {}


def getDirList(path, DirList):
	for item in os.listdir(path):
		# if os.path.isfile(os.path.join(path, item)):
		# 	FileList.append(item)
		if not item.startswith('.') and os.path.isdir(os.path.join(path, item)):
			getDirList(path+item+'/', DirList)
			DirList.append(path+item+'/')
	return

def perDirFileList(path, FileList):
	for item in os.listdir(path):
		if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
			FileList.append(item)
	return FileList

def parseVocab(path):
	global indexV
	global Vocab
	f = open(path)
	Lines = f.readlines()
	f.close()

	UnigramList = []

	for line in Lines:
		trantab = string.maketrans('@.,','   ')
		delEStr = "!\"#$%&'()*+-/:;<=>?[\]^_`{|}~"
		line = line.translate(trantab, delEStr)
		# exclude 	= set(string.punctuation)
		# line		= ''.join(ch for ch in line if ch not in exclude )
		UnigramList = line.lower().strip().split(' ')
		for Unigram in UnigramList:
			if Unigram.isalpha() and not Unigram in CommonWords:
				if not Unigram in Vocab:
					Vocab[Unigram] = indexV
					indexV += 1


def parseToSklnFmt(path):
	tmpDic = {}
	UnigramList = []
	global Vocab
	VocabNumber = 0

	f = open(path)
	Lines = f.readlines()
	f.close()

	UnigramList = []

	for line in Lines:
		trantab = string.maketrans('@.,','   ')
		delEStr = "!\"#$%&'()*+-/:;<=>?[\]^_`{|}~"
		line = line.translate(trantab, delEStr)
		# exclude 	= set(string.punctuation)
		# line		= ''.join(ch for ch in line if ch not in exclude )
		UnigramList = line.lower().strip().split(' ')
		for unigram in UnigramList:

			if unigram.isalpha() and not unigram in CommonWords:
				VocabNumber = Vocab.get(unigram)
	        	if VocabNumber != None and VocabNumber != 0:
	        		if VocabNumber in tmpDic:
	        			tmpDic[VocabNumber] += 1
	        		else:
	        			tmpDic[VocabNumber] = 1


	tmpDic = OrderedDict( sorted(tmpDic.items() ) )
	# print '\n'
	# print path, tmpDic
	return tmpDic

##################################################################################################################

getDirList(path, TopicList)
TopicList += ["./20news/Test/"]

for topic in TopicList:
	print topic
	FileList = []
	FileList = perDirFileList(topic, FileList)
	for file in FileList:
		parseVocab(topic + file)


# print Vocab
print len(Vocab)
#89872

##################################################################################################################








index = 0
outPutString = ""
TopicList = []
fo = open(outputPath+"/train.txt", 'wb+')
getDirList("./20news/Train/", TopicList)
for topic in TopicList:
	FileList = []
	perDirFileList(topic, FileList)
	for file in FileList:
		fo.write(str(index) + ' ')
		DicPerFile = parseToSklnFmt(topic + file)

		for key in DicPerFile:
			fo.write(' ' + str(key) + ":" + str(DicPerFile[key]))

		fo.write('\n')
	index += 1
fo.close()




index = 0
score = 0
f = open('ans.test.txt')
anslist = f.readlines()
f.close()
topicnumbers = []
for ans in anslist:
	qq = ans.strip().split(' ')
	topicnumbers.append(TopicList.index('./20news/Train/' + qq[1] + '/'))
	# print qq[0], 




fo = open(outputPath+"/test.txt", 'wb+')
FileList = []
perDirFileList("./20news/Test/", FileList)

for file in FileList:
	fo.write(str(topicnumbers[index]) + " ")
	writeout = parseToSklnFmt("./20news/Test/" + file)
	for word in writeout:
		fo.write(' ' + str(word) + ":" + str(writeout[word]))
	index += 1
	fo.write('\n')
fo.close()

