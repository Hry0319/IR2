# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import numpy as np
import sqlite3
# sys.setrecursionlimit(10000)

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
	for item in os.listdir(path):
		if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
			FileList.append(item)
			## for vocab parse
			AllFilePaths.append(path + item)


def parseVocab():
	for file in AllFilePaths:
		f = open(file)
		Lines = f.readlines()
		f.close()

		for line in Lines:
			wordslist = line.lower().strip().split(' ')

			for word in wordslist:

				if word.isalpha(): 
					#print word
					if not dic.has_key(word):
						dic[word] = 1
					else:
						dic[word] += 1

	return



path       = "../20news/"
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
# f = open('./' + 'vocab.txt', 'a')
# for vocab in dic:
# 	# print vocab, dic[vocab]
# 	f. write(vocab +' '+ str(dic[vocab]) + '\n')
# f.flush()
# f.close()

# print dic['to']








