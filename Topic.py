# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import numpy as np
import sqlite3

commonWords = ('more','article','i','the','be','am','to','of','and','a','in','that','has','have','had','no','an','been','not','it','is','im','are','were','was','for','on','with','he','as','you','do','does','at','this','but','his','by','from','they','we','say','her','she','or','an','will','my','one','all','would','there','their','what','so','up','out','if','about','who','get','which','go','me','when','make','can','like','time','just','him','know','take','person','into','year','your','some','could','them','see','other','than','then','now','look','only','come','its','over','think','also','back','after','use','two','how','our','way','even','because','any','these','us')


'''
SQLite table
{
	Topic:
		TopicName       # !!! the diff Topics may have same unigram!!! 
		Unigram
		Probility
		WordsCount      # per unigram
}

'''

class Topic:
	Label	    = ""    # topic folder dir name 
	UnigramProb = {}    # dictionary
	WordsCount  = 0		# totally words count of Topic

	def CalProbPerUnigram(self, FileList):
		"""
		FileList from only one Topic Folder within the file path
		"""
		for file in FileList:
			f = open(file)
			Lines = f.readlines()
			f.close()

			for line in Lines:
				wordslist = line.lower().strip().split(' ')

				for Unigram in wordslist:

					if Unigram.isalpha() and Unigram not in commonWords:
						self.WordsCount += 1

						if not self.UnigramProb.has_key(Unigram):
							self.UnigramProb[Unigram] = 1
						else:
							self.UnigramProb[Unigram] += 1.0

		#print self.UnigramProb
		
		c = self.conn.cursor()
		for unigram in self.UnigramProb:
			#self.UnigramProb[unigram] /= self.WordsCount
			sqlcmd = "INSERT INTO Topic VALUES (%s, %s, %f, %d)" % ('\''+self.Label+'\'', '\''+unigram+'\'', self.UnigramProb[unigram]/self.WordsCount, self.UnigramProb[unigram])
			#print sqlcmd
			c.execute(sqlcmd)
		c.close()
		self.conn.commit()


		print self.WordsCount

		return





	def __init__(self, label):
		self.conn = sqlite3.connect('./Topic.db')

		self.Label = label
		return

	def reset(self):
		c = self.conn.cursor()
		try:
			c.execute('delete from Topic')

		finally:
			c.close()
			self.conn.commit()