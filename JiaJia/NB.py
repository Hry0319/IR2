#!/usr/bin/env python
import numpy as np
from sklearn.datasets import load_svmlight_file
from sklearn.naive_bayes import MultinomialNB
import sys

X_train, Y_train = load_svmlight_file("train.txt", n_features=sys.argv[1] )
print X_train.shape
X_test, Y_test = load_svmlight_file("test.txt")
print X_test.shape

clf = MultinomialNB()
clf.fit(X_train, Y_train)

correct = 0.0
Y_predict = clf.predict(X_test)
for i, Y in enumerate(Y_predict):
    if Y == Y_test[i]:
        correct += 1

print correct/len(Y_test)
