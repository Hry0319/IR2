# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3
# import scipy
import numpy as np

dic 	   = {}
path       = "../20news/"
outputPath = "./JiaJia/"
TopicList  = []
FileList   = []


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


