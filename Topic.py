# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3
import numpy as np
from collections import OrderedDict

CommonWords = ('','more','article','i','the','be','am','to','of','and','a','in','that','has','have','had',
	'no','an','been','not','it','is','im','are','were','was','for','on','with','he','as','you','do','does',
	'at','this','but','his','by','from','they','we','say','her','she','or','an','will','my','one','all','would',
	'there','their','what','so','up','out','if','about','who','get','which','go','me','when','make','can','like',
	'time','just','him','know','take','person','into','year','your','some','could','them','see','other','than','then',
	'now','look','only','come','its','over','think','also','back','after','use','two','how','our','way','even','because',
	'any','these','us')

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
	UnigramCount 	 = {}    # dictionary !!!  (O) OrderedDict   (X) this dictionary will transform to be a sorted List
	TopicWordsCount  = 0		# totally words count of Topic
	TopicProbability = 0.0     # the TopicProbability of P(Topic), the TopicProbability for each Topic
	VocabCount       = 0

	def SelectUnigramFromDB(self):
		"""
		Be sure your DB is not empty
		"""
		self.TopicWordsCount= 0
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
		self.UnigramCount = OrderedDict(sorted(self.UnigramCount.items(), key=lambda x: x[1], reverse = True))
		self.VocabCount = len(self.UnigramCount )
		

	def CalProbPerUnigram(self, FileList):
		"""
		FileList from only one Topic Folder within the file path
		"""
		for file in FileList:
			f = open(file)
			Lines = f.readlines()
			f.close()

			for line in Lines:
				trantab = string.maketrans('','')
				delEStr = string.punctuation
				line = line.translate(trantab, delEStr)

				wordslist = line.lower().strip().split(' ')

				for Unigram in wordslist:					
					if Unigram.isalpha() and Unigram not in CommonWords:
						self.TopicWordsCount+= 1
						if not self.UnigramCount.has_key(Unigram):
							self.UnigramCount[Unigram] = 1
						else:
							self.UnigramCount[Unigram] += 1.0

		c = self.conn.cursor()
		for unigram in self.UnigramCount:

			prob = self.UnigramCount[unigram]/self.TopicWordsCount
			if prob != 0 :
				# prob = np.log(prob)
				''' do nothing '''
			else:
				# prob = -9.6
				prob = float(3.25e-05)
			sqlcmd = "INSERT INTO Topic VALUES(%s, %s, %f, %d)" % ('\''+self.Label+'\'', '\''+unigram+'\'', prob, self.UnigramCount[unigram])
			c.execute(sqlcmd)
		c.close()
		self.conn.commit()

		#
		# Sort dictionary by value
		#
		# self.UnigramCount = sorted(self.UnigramCount.iteritems(), key=lambda (k,v): (v,k))[0:15]  // this will be list or tuple
		self.UnigramCount = OrderedDict(sorted(self.UnigramCount.items(), key=lambda x: x[1], reverse = True))
		self.VocabCount = len(self.UnigramCount )

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
