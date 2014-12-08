import operator
import json
import numpy as np
from sklearn.naive_bayes import MultinomialNB as mnb
import loadData
import wordvectors

# Get top tags. Diction of <int, int>: tagID to count in first 50,000 questions
# Only includes tags which appeared more than 50 times.
tcount_infile = open('tcount-50000.txt', 'r')
tempTopTags = json.load(tcount_infile)
tcount_infile.close()
topTags = {}
for idStr, count in tempTopTags.items():
  topTags[int(idStr)] = count

def normalizeProb(tagProbD):
  maxProb = tagProbD[max(tagProbD, key=lambda x: tagProbD[x])]
  minProb = tagProbD[min(tagProbD, key=lambda x: tagProbD[x])]
  for tag in tagProbD:
    tagProbD[tag] = (tagProbD[tag] - minProb)/(maxProb - minProb)

def recall_k(k, topTags, actualTags):
  recall_score = 0.0
  for i in xrange(k):
    if topTags[i] in actualTags:
      recall_score += 1.0
  return recall_score / len(actualTags)

def multinomialNaiveBayesTrain(trainQuestions, tag, X, y, mnbd):
  clf = mnb()
  i = 0
  for qid in trainQuestions:
    if tag in trainQuestions[qid].tags:
      y[i] = 1
    else:
      y[i] = 0
    i += 1

  clf.fit(X,y)
  mnbd[tag] = clf

"""
Trains multinomial naive bayes models for each tag and stores them
in a dict that is returned
"""
def getTagNaiveBayesScores(trainQuestions, topTags, wordToIndex, wordVecs):
  mnbd = {}
  X = np.zeros((len(trainQuestions), len(wordToIndex)))
  y = np.zeros(len(trainQuestions))
  i = 0
  for qid in trainQuestions:
    X[i] = np.array(wordVecs[qid])
    i += 1
  for t in topTags:
    multinomialNaiveBayesTrain(trainQuestions, t, X, y, mnbd)
  X = np.zeros(1)
  return mnbd

"""
Returns a normalized probability dictionary of relevant tags for
an input question
"""
def getProbForQuestion(qid, mnbd, topTags, wordVecs):
  questionNBD = {}
  for tag in topTags:
    clf = mnbd[tag]
    X = np.array(wordVecs[qid])
    tagProb = clf.predict_proba(X)
    questionNBD[tag] = tagProb[0][1]
  normalizeProb(questionNBD)
  return questionNBD

def modelNaiveBayes(testQuestions, mnbd, topTags, wordVecs):
  numTest = len(testQuestions)
  recall_5_sum = 0.0
  recall_10_sum = 0.0
  i = 0
  for (qid, question) in testQuestions.items():
    if i % 1000 == 0:
      print i
    tagD = getProbForQuestion(qid, mnbd, topTags, wordVecs)
    sortedTags = sorted(tagD, key=lambda x: tagD[x], reverse=True)
    num = min(10, len(sortedTags))
    bestTags = sortedTags[0:num]
    recall_5 = recall_k(5, bestTags, question.tags)
    recall_10 = recall_k(10, bestTags, question.tags)
    recall_5_sum += recall_5
    recall_10_sum += recall_10
    i += 1
  recall_5_avg = recall_5_sum / numTest
  recall_10_avg = recall_10_sum / numTest
  return recall_5_avg, recall_10_avg
"""
for fold in folds:
  trainQuestions = fold[0]
  mnbd = getTagNaiveBayesScores(trainQuestions, topTags, wordToIndex, wordVecs)
  print "Training Naive Bayes Completed"
  testQuestions = fold[1]
  recall_5, recall_10 = modelNaiveBayes(testQuestions, mnbd, topTags, wordVecs)
  print recall_5
  print recall_10"""


