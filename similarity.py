import math
import numpy as np
import random
from collections import defaultdict


def computeIdf(wordVectors):
  numWords = len(wordVectors.itervalues().next())
  numDocs = len(wordVectors)
  idf = np.zeros(numWords)
  for id, vector in wordVectors.iteritems():
    idf += (vector > 0).astype(int)
  idf = math.log(numDocs) - np.log(idf)
  return idf

def computeTfIdf(wordVector, idf):
  tf = wordVector  # raw frequences, can change to other things
  return tf * idf

def computeTfIdfs(wordVectors, idf):
  tfidfs = {}
  for id, vector in wordVectors.iteritems():
    tfidfs[id] = computeTfIdf(vector, idf)
  return tfidfs

def computeCosSim(trainTfIdf, testTfIdf):
  numWords = len(trainTfIdf)
  trainNorm = np.linalg.norm(trainTfIdf)
  testNorm = np.linalg.norm(testTfIdf)
  if trainNorm == 0 or testNorm == 0:
    return 0.0
  similarity = np.dot(trainTfIdf, testTfIdf)
  return similarity/(trainNorm * testNorm)

def findSimilarPosts(trainTfIdfs, testTfIdf, num):
  similarities = {}
  for id, trainTfIdf in trainTfIdfs.iteritems():
    similarities[id] = computeCosSim(trainTfIdf, testTfIdf)
  sortedKeys = sorted(trainTfIdfs, key=lambda id : similarities[id], reverse=True)
  topPosts = sortedKeys[0:num]
  return topPosts

def findSimilarTags(topPosts, num):
  tagVotes = defaultdict(float)
  totalVotes = 0
  for id in topPosts:
    question = questions[id]
    for tagId in question.tags:
      tagVotes[tagId] += 1
      totalVotes += 1
  sortedKeys = sorted(tagVotes, key=lambda id : tagVotes[id], reverse=True)
  topTags = sortedKeys[0:num]
  likelihoods = np.empty(num)
  for i in xrange(num):
    likelihoods[i] = tagVotes[topTags[i]] * 1.0 / totalVotes
  return topTags, likelihoods

def recall_k(k, topTags, actualTags):
  recall_score = 0.0
  for i in xrange(k):
    if topTags[i] in actualTags:
      recall_score += 1.0
  return recall_score / len(actualTags)

def similarityModel(trainVectors, testVectors, numPosts, numTags):
  print "computing idf"
  idf = computeIdf(trainVectors)
  print "idf done"
  print "computing tfidfs"
  tfidfs = computeTfIdfs(trainVectors, idf)
  print "tfidfs done"
  numTest = len(testVectors)
  recall_5_sum = 0.0
  recall_10_sum = 0.0
  for id, testVector in testVectors.iteritems():
    testTfIdf = computeTfIdf(testVector, idf)
    topPosts = findSimilarPosts(tfidfs, testTfIdf, numPosts)
    topTags, likelihoods = findSimilarTags(topPosts, numTags)
    recall_5 = recall_k(5, topTags, questions[id].tags)
    recall_10 = recall_k(10, topTags, questions[id].tags)
    recall_5_sum += recall_5
    recall_10_sum += recall_10
    print recall_5, recall_10

  return recall_5_sum/numTest, recall_10_sum/numTest



# trainVecs = {}
# testVecs = {}
# random.seed(1)
# for id, vector in wordVecs.iteritems():
#   num = random.random()
#   if num > 0.999:
#     testVecs[id] = vector
#   else:
#     trainVecs[id] = vector
# avg_5, avg_10 = similarityModel(trainVecs, testVecs, 50, 10)
'''
results
>>> avg_5
0.4771241830065359
>>> avg_10
0.5810457516339869
'''




