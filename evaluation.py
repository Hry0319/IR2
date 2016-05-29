# -*- coding: utf-8 -*-
import os
import io
import sys
import gc
import string
import sqlite3
import numpy as np



def main():  
	score = 0

	f = open('ans.test.txt')
	ans = f.readlines()
	f.close()

	f = open('output.txt')
	output = f.readlines()
	f.close()

	for i in xrange(0, len(output)):
		if ans[i] == output[i]:
			score+=1


	print "!! score : %d" % score

	return










# main()
if __name__ == '__main__':
    main()
    