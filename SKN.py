# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3
# import scipy
import numpy as np


CommonWords = ('',
	'more','article','i','the','be','am','to','of','and','a','in','that','has','have','had',
	'no','an','been','not','it','is','im','are','were','was','for','on','with','as','you','do','does',
	'at','this','but','by','from','or','an','will','my','one','all','would',
	'there','their','what','so','up','out','if','about','who','get','which','go','me','when','make','can','like',
	'just','take','into','year','your','some','them','see','other','than','then',
	'look','only','come','its','over','also','back','after','use','two','how','our','even',
	'any','these','us',)
	# 'now','they','we','say','her','she','time','know','person','think','way','his','he','him','could','because',)

Vocab 	   		= {}
path       		= "../20news/Train/"
outputPath 		= "./JiaJia/Train/"
TopicList  		= []
AllFilePaths 	= []


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
			## for vocab parse
			AllFilePaths.append(path + item)
	return

def parseVocab(path, index):
	f = open(path)
	Lines = f.readlines()
	f.close()

	for line in Lines:
		trantab = string.maketrans('\n\'\"@#$%^&*()_','   @         ')
        delEStr = string.punctuation
        line 	= line.translate(trantab, delEStr)
        UnigramList = line.lower().split(' ')

        for Unigram in UnigramList:
            if Unigram not in CommonWords:
            	if not Vocab.has_key(Unigram):
            		index += 1
            		Vocab[Unigram] = index
            		# print index , 


	return index

def parseToSknFmt(path):	
	f = open(path)
	Lines = f.readlines()
	f.close()

	TestDataUnigramList = []

	# print path
	for line in Lines:
		trantab = string.maketrans('','')
        delEStr = string.punctuation
        line 	= line.translate(trantab, delEStr)
        UnigramList = line.lower().strip().split(' ')

        for Unigram in UnigramList:
            if Unigram.isalpha() and Unigram not in CommonWords:
            	""""""


getDirList(path, TopicList)
index = 0

for topic in TopicList:

	FileList = []
	perDirFileList(topic, FileList)

	for file in FileList:
		index = parseVocab(topic + file, index)

print Vocab


# AllFilePaths 	= []
# for topic in TopicList:

# 	FileList = []
# 	perDirFileList(topic, FileList)

# 	for file in FileList:
# 		parseToSknFmt(topic + file)














