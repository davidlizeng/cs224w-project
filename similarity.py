import math
import numpy as np
import random
from collections import defaultdict
import wordvectors
import heapq
import time


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

def findSimilarPosts(trainTfIdfs, ids, testTfIdf, num):
  heap = []
  cosines = trainTfIdfs.dot(testTfIdf)
  for i in xrange(len(ids)):
    similarity = cosines[i]
    if len(heap) < num:
      heapq.heappush(heap, (similarity, ids[i]))
    else:
      heapq.heappushpop(heap, (similarity, ids[i]))
  topPosts = [x[1] for x in heap]
  return topPosts

def findSimilarTags(topPosts, questions):
  tagVotes = defaultdict(float)
  totalVotes = 0
  for id in topPosts:
    question = questions[id]
    for tagId in question.tags:
      tagVotes[tagId] += 1
      totalVotes += 1
  for id in tagVotes:
    tagVotes[id] /= totalVotes
  return tagVotes

def recall_k(k, sortedTags, result, actualTags):
  recall_score = 0.0
  for i in xrange(k):
    if result[sortedTags[i]] > 0 and sortedTags[i] in actualTags:
      recall_score += 1.0
  return recall_score / len(actualTags)


# sim_data = None


# def initSimModel():
#   global sim_data
#   if sim_data == None:
#     sim_data = {}
#     print "no sim data detected. generating/caching word vectors"
#     words, wordToIndex = wordvectors.getFrequentWords(questions)
#     wordVecs = wordvectors.getWordVectors(questions, wordToIndex)
#     sim_data['wordToIndex'] = wordToIndex
#     sim_data['wordVecs'] = wordVecs


def similarityModel(questions, wordVecs):
  trainVectors = {}
  for id in questions:
    trainVectors[id] = wordVecs[id]
  # print "computing idf"
  idf = computeIdf(trainVectors)
  # print "idf done"
  # print "computing tfidfs"
  tfidfs = computeTfIdfs(trainVectors, idf)
  tfidf_matrix = np.zeros((len(tfidfs), len(tfidfs.itervalues().next())), dtype='float64')
  ids = tfidfs.keys()
  for i in xrange(len(ids)):
    norm = np.linalg.norm(tfidfs[ids[i]])
    if norm != 0:
      tfidf_matrix[i] = tfidfs[ids[i]] / norm
  # print "tfidfs done"
  return (tfidf_matrix, ids, idf)


def getSimilarityRankingScores(questionId, questions, wordVecs, sim_model, tagCounts):
  numPosts = 5
  # postWords = wordvectors.getWordsFromPost(questionBody)
  tfidfs = sim_model[0]
  ids = sim_model[1]
  idf = sim_model[2]

  # testVector = wordvectors.getWordVector(postWords, wordToIndex)
  testVector = wordVecs[questionId]
  testTfIdf = computeTfIdf(testVector, idf)
  norm = np.linalg.norm(testTfIdf)

  if norm != 0:
    testTfIdf /= norm

  # print "test tfidf finished"
  topPosts = findSimilarPosts(tfidfs, ids, testTfIdf, numPosts)
  # print "top posts found"
  likelihoods = findSimilarTags(topPosts, questions)
  # print "likelihoods found"

  result = {}
  l_values = likelihoods.values()
  min_val = min(l_values)
  range_val = max(l_values) - min_val
  for tagId in tagCounts.keys():
    if tagId in likelihoods and range_val > 0:
      result[tagId] = (likelihoods[tagId] - min_val)/range_val
    else:
      result[tagId] = 0.0
  return result


def run():
  folds = getCVFolds()
  train = folds[0][0]
  test = folds[0][1]
  t0 = time.time()
  sim_model = similarityModel(train)
  t1 = time.time()
  print "train complete", t1 - t0
  t2 = time.time()
  recall5_sum = 0
  recall10_sum = 0
  count = 0
  for qid in test:
    result = getSimilarityRankingScores(qid, sim_model, topTags)
    sortedTags = sorted(result, key = result.get, reverse = True)
    recall5 = recall_k(5, sortedTags, result, questions[qid].tags)
    recall10 = recall_k(10, sortedTags, result, questions[qid].tags)
    recall5_sum += recall5
    recall10_sum += recall10
    print qid, recall5, recall10, count
    count += 1
  t3 = time.time()
  print "test complete", t3 - t2
  print "MEAN: ",  recall5_sum/5000.0, recall10_sum/5000.0

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




