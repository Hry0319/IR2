 # -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3
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

"""  
CREATE TABLE 'Topic' ('TopicName' CHAR DEFAULT '""', 'Unigram' CHAR DEFAULT '""', 'Probability' DOUBLE DEFAULT '0', 'WordsCount' INTEGER DEFAULT '0')

SQLite table
{
	Topic:
		TopicName       # !!! the diff Topics may have same unigram!!!
		Unigram 		# Unigram name
		Probability     # Unigram Probability
		WordsCount      # per unigram
}
"""

class TopicModel:
	Label	     	 = ""    # topic folder dir name
	UnigramCount 	 = {}    # dictionary : (O) OrderedDict   (X) this dictionary will transform to be a sorted List
	UnigramProb      = {}    # dictionary : [ Additive Smoothing ]
	TopicWordsCount  = 0		# totally words count of Topic
	TopicProbability = 0.0     # the TopicProbability of P(Topic), the TopicProbability for each Topic
	VocabCount       = 0
	Zeta             = 0.5

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
			self.TopicWordsCount+= int(row[3])
		c.close()

		#
		# Sort dictionary by value
		# transform to List
		#
		# self.UnigramCount = sorted(self.UnigramCount.iteritems(), key=lambda d:d[1], reverse = True)[0:15]  // this will be list or tuple
		# self.UnigramCount = OrderedDict(sorted(self.UnigramCount.items(), key=lambda x: x[1], reverse = True))
		self.VocabCount = 32648 #len(self.UnigramCount )    #XXXXX  not per topic , plz use the total corpus

		#
		# try smooth   additive => 0.5
		#
		for unigram in self.UnigramCount:
			zeta = self.Zeta
			self.UnigramProb[unigram] = (self.UnigramCount[unigram] + zeta) / (self.TopicWordsCount + self.VocabCount * zeta)


	def CalProbPerUnigram(self, FileList):
		"""
		FileList from only one Topic Folder within the file path
		"""
		for file in FileList:
			f = open(file)
			Lines = f.readlines()
			f.close()

			for line in Lines:
				trantab 	= string.maketrans('@.,','   ')
				delEStr 	= "!\"#$%&'()*+-/:;<=>?[\]^_`{|}~"
				line 		= line.translate(trantab, delEStr)
				wordslist 	= line.lower().strip().strip().split(' ')
				for Unigram in wordslist:					
					if Unigram.isalpha() and not Unigram in CommonWords:
						self.TopicWordsCount+= 1
						if not Unigram in self.UnigramCount:
							self.UnigramCount[Unigram] = 1.0
						else:
							self.UnigramCount[Unigram] += 1.0

		c = self.conn.cursor()
		for unigram in self.UnigramCount:

			prob = self.UnigramCount[unigram]/self.TopicWordsCount
			# if prob != 0 :
			# 	# prob = np.log(prob)
			# 	''' do nothing '''
			# else:
			# 	# prob = -9.6
			# 	prob = float(3.25e-05)
			sqlcmd = "INSERT INTO Topic VALUES(%s, %s, %f, %d)" % ('\''+self.Label+'\'', '\''+unigram+'\'', prob, self.UnigramCount[unigram])
			c.execute(sqlcmd)
		c.close()
		self.conn.commit()

		#
		# Sort dictionary by value
		#
		# self.UnigramCount = sorted(self.UnigramCount.iteritems(), key=lambda (k,v): (v,k))[0:15]  // this will be list or tuple
		# self.UnigramCount = OrderedDict(sorted(self.UnigramCount.items(), key=lambda x: x[1], reverse = True))
		self.VocabCount = 32648 #len(self.UnigramCount )   #XXXXX  not per topic , plz use the total corpus

		#
		# try smooth   additive => 0.5
		#
		for unigram in self.UnigramCount:
			zeta = self.Zeta
			self.UnigramProb[unigram] = (self.UnigramCount[unigram] + zeta) / (self.TopicWordsCount + self.VocabCount * zeta)

	def SQL_SUM(self):
		# get TopicWordsCountfrom DB
		c = self.conn.cursor()
		sqlcmd2 = "SELECT SUM(WordsCount) FROM Topic where TopicName='%s'" % (self.Label)
		c.execute(sqlcmd2)
		print self.Label, int(c.fetchone()[0]), self.TopicWordsCount

	def __init__(self, label):
		self.conn 			 = sqlite3.connect('./Topic.db')
		self.Label 			 = label
		self.TopicWordsCount = 0
		self.UnigramCount 	 = {}

	def reset(self):
		c = self.conn.cursor()
		try:
			c.execute('delete from Topic')
		finally:
			c.close()
			self.conn.commit()
