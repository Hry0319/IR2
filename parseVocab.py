# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import numpy as np
import sqlite3
# sys.setrecursionlimit(10000)
CommonWords = ('all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should',
	 'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did', 
	 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 'out', 'what', 
	 'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about', 'of', 
	 'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too', 
	 'themselves', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself', 
	 'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have', 
	 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after', 'most', 'such', 'why', 'a', 
	 'off', 'i', 'yours', 'so', 'the', 'having', 'once'
	)
dic = {}

def getDirList(path, DirList):
	for item in os.listdir(path):
		# if os.path.isfile(os.path.join(path, item)):
		# 	FileList.append(item)
		if not item.startswith('.') and os.path.isdir(os.path.join(path, item)):

			getDirList(path+item+'/', DirList)
			DirList.append([path+item+'/'])

	return


AllFilePaths = []
def perDirFileList(path, FileList):
	global AllFilePaths
	for item in os.listdir(path):
		if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
			FileList.append(item)
			## for vocab parse
			AllFilePaths.append(path + item)


def parseVocab():
	global dic
	global CommonWords
	for file in AllFilePaths:
		f = open(file)
		Lines = f.readlines()
		f.close()

		for line in Lines:			
			trantab 	= string.maketrans('@.,','   ')
			delEStr 	= "!\"#$%&'()*+-/:;<=>?[\]^_`{|}~"
			line 		= line.translate(trantab, delEStr)
			wordslist 	= line.lower().strip().split(' ')
			for word in wordslist:
				if word.isalpha() and word not in CommonWords:
					#print word
					if not dic.has_key(word):
						dic[word] = 1
					else:
						dic[word] += 1

	return



path       = "./20news/Train/"
TopicList  = []
FileList   = []



# 1 get dir
getDirList(path, TopicList)
print TopicList

# 2 per dir file list
for dir in TopicList:
	perDirFileList(dir[0], FileList)
	dir.append(FileList)

# 3 parse vocab 
parseVocab()

# 4 write to file 
f = open('./' + 'vocab.txt', 'wb+')
for vocab in dic:
	# print vocab, dic[vocab]
	f. write(vocab +' '+ str(dic[vocab]) + '\n')
f.flush()
f.close()

# print dic['to']

print len(dic)








