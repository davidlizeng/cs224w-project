import json
import numpy as np
import loadData
import bipartite

# Get top tags. Diction of <int, int>: tagID to count in first 50,000 questions
# Only includes tags which appeared more than 50 times.
tcount_infile = open('tcount-50000.txt', 'r')
tempTopTags = json.load(tcount_infile)
tcount_infile.close()
topTags = {}
for idStr, count in tempTopTags.items():
  topTags[int(idStr)] = count

userGraph = {}
alpha = 0.6
beta = 0.0
gamma = 0.2
delta = 0.4

def normalizeScores(tagPredict):
  maxScore = tagPredict[max(tagPredict, key=lambda x: tagPredict[x])]
  minScore = tagPredict[min(tagPredict, key=lambda x: tagPredict[x])]
  for tag in tagPredict:
    if maxScore == minScore:
      tagPredict[tag] = 0
    else:
      tagPredict[tag] = (tagPredict[tag] - minScore)/(maxScore - minScore)

def recall_k(k, bestTags, actualTags):
  recall_score = 0.0
  for i in xrange(k):
    if bestTags[i] in actualTags:
      recall_score += 1.0
  return recall_score / len(actualTags)

def createUserGraph(trainQuestions):
  userGraph = bipartite.getGraph(loadData.users, trainQuestions, loadData.answers, loadData.comments)
  return userGraph
  
def getTagPredictions(qid, question, userGraph, topTags):
  bestAnswerId = question.bestAnswerId
  answers = question.answers
  comments = question.comments

  tagPredict = {}
  for tag in topTags:
    tagScore = 0
    if tag in userGraph[question.userId]:
      tagScore += alpha * userGraph[question.userId][tag]
    """if question.bestAnswerId:
      if tag in userGraph[loadData.answers[question.bestAnswerId].userId]:
        tagScore += beta * userGraph[loadData.answers[question.bestAnswerId].userId][tag]"""
    for cid in comments:
      comment = loadData.comments[cid]
      if tag in userGraph[comment.userId]:
        tagScore += gamma * userGraph[comment.userId][tag]
    for aid in answers:
      answer = loadData.answers[aid]
      if tag in userGraph[answer.userId]:
        tagScore += delta * userGraph[answer.userId][tag]
    tagPredict[tag] = tagScore
  normalizeScores(tagPredict)
  return tagPredict

def modelUserGraph(testQuestions, userGraph, topTags):
  numTest = len(testQuestions)
  recall_5_sum = 0.0
  recall_10_sum = 0.0
  for (qid, question) in testQuestions.items():
    tagD = getTagPredictions(qid, question, userGraph, topTags)
    sortedTags = sorted(tagD, key=lambda x: tagD[x], reverse=True)
    num = min(10, len(sortedTags))
    bestTags = sortedTags[0:num]
    recall_5 = recall_k(5, bestTags, question.tags)
    recall_10 = recall_k(10, bestTags, question.tags)
    recall_5_sum += recall_5
    recall_10_sum += recall_10
  recall_5_avg = recall_5_sum / numTest
  recall_10_avg = recall_10_sum / numTest
  return recall_5_avg, recall_10_avg
"""
bestRecall5 = 0
bestRecall10 = 0
bestAlpha5 = 0
bestBeta5 = 0
bestGamma5  = 0
bestDelta5 = 0
bestAlpha10 = 0
bestBeta10 = 0
bestGamma10  = 0
bestDelta10 = 0
#BEST RECALL@5 :0.342433333333
#BEST RECALL@5 PARAMETERS: (0.800000, 0.000000, 0.200000, 0.400000)
#BEST RECALL@10 :0.41831
#BEST RECALL@10 PARAMETERS: (0.600000, 0.000000, 0.200000, 0.400000)
for fold in folds:
  trainQuestions = fold[0]
  userGraph = createUserGraph(trainQuestions)
  testQuestions = fold[1]
  for alpha in xrange(6):
    alpha = alpha * 0.2
    for beta in xrange(1):
      beta = beta * 0.2
      for gamma in xrange(6):
        gamma = gamma * 0.2
        for delta in xrange(6):
          delta = delta * 0.2
          alpha = 0.6
          beta = 0.0
          gamma = 0.2
          delta = 0.4
          recall_5, recall_10 = modelUserGraph(testQuestions, userGraph, topTags)
          if recall_5 > bestRecall5:
            bestRecall5 = recall_5
            bestAlpha5 = alpha
            bestBeta5 = beta
            bestGamma5 = gamma
            bestDelta5 = delta
          if recall_10 > bestRecall10:
            bestRecall10 = recall_10
            bestAlpha10 = alpha
            bestBeta10 = beta
            bestGamma10 = gamma
            bestDelta10 = delta
          print 'Parameters: (%f, %f, %f, %f)' % (alpha, beta, gamma, delta)
          print 'recall@5 score: ' + str(recall_5)
          print 'recall@10 score: ' + str(recall_10)
  print 'BEST RECALL@5 :' + str(bestRecall5)
  print 'BEST RECALL@5 PARAMETERS: (%f, %f, %f, %f)' % (bestAlpha5, bestBeta5, bestGamma5, bestDelta5)
  print 'BEST RECALL@10 :' + str(bestRecall10)
  print 'BEST RECALL@10 PARAMETERS: (%f, %f, %f, %f)' % (bestAlpha10, bestBeta10, bestGamma10, bestDelta10)
"""

