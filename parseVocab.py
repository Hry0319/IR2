# -*- coding: utf-8 -*-
#from __future__ import print_function  # Py 2.6+; In Py 3k not needed
import os
import io
import sys
import gc
import numpy as np

# sys.setrecursionlimit(10000)

def getDirList(path, DirList):
	for item in os.listdir(path):
		# if os.path.isfile(os.path.join(path, item)):
		# 	FileList.append(item)
		if not item.startswith('.') and os.path.isdir(os.path.join(path, item)):	
			DirList.append([item])


AllFilePaths = []
def perDirFileList(path, Dir, FileList):
	for item in os.listdir(path + Dir):
		FileList.append(item)
		## for vocab parse
		AllFilePaths.append(path + Dir + '/' + item)



path       = "../20news/Train/"
TopicList  = []
FileList   = []



# 1 get dir
getDirList(path, TopicList)

# 2 per dir file list
for dir in TopicList:
	perDirFileList(path, dir[0], FileList)
	dir.append(FileList)













