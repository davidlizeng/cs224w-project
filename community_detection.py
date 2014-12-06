import snap
import numpy as np
import random
from collections import defaultdict


def getUsersSubset(users, questions, answers, comments):
  subset = {}
  for id, question in questions.iteritems():
    userId = question.userId
    if userId not in subset:
      subset[userId] = users[userId]
  for id, answer in answers.iteritems():
    userId = answer.userId
    if userId not in subset:
      subset[userId] = users[userId]
  for id, comment in comments.iteritems():
    userId = comment.userId
    if userId not in subset:
      subset[userId] = users[userId]
  return subset


def createUsersGraph(users, questions, answers, comments):
  graph = snap.TUNGraph.New()
  for id, user in users.iteritems():
    graph.AddNode(id)
  for id, question in questions.iteritems():
    quid = question.userId
    for aid in question.answers:
      answer = answers[aid]
      auid = answer.userId
      if auid != quid and answer.score > 1:
        graph.AddEdge(auid, quid)
  return graph

def recall_k(k, topTags, actualTags):
  recall_score = 0.0
  num = min(len(topTags), k)
  for i in xrange(num):
    if topTags[i] in actualTags:
      recall_score += 1.0
  return recall_score / len(actualTags)

def getComms(graph):
  comms = snap.TCnComV()
  modularity = snap.CommunityCNM(graph, comms)
  print 'Modularity', modularity
  commDict = {}
  for i in xrange(len(comms)):
    for id in comms[i]:
      if id in commDict:
        'node in more than one comm?'
      else:
        commDict[id] = i
  return comms, commDict

def commModelWithSim(testSet, comms, commDict, wordVecs):
  recall_5_sum = 0.0
  recall_10_sum = 0.0
  for id, question in testSet.iteritems():
    votes = defaultdict(float)
    user = users[question.userId]
    comm = comms[commDict[user.id]]
    for nid in comm:
      nbr = users[nid]
      for qid in nbr.questions:
        if qid == id:
          continue
        # n1 = np.linalg.norm(wordVecs[id])
        # n2 = np.linalg.norm(wordVecs[qid])
        # if n1 == 0 or n2 == 0:
        #   similarity = 0
        # else:
        #   similarity = np.dot(wordVecs[id], wordVecs[qid])/(n1 * n2)
        #   similarity = (similarity + 1)/2
        for tid in questions[qid].tags:
          votes[tid] += 1
    sortedKeys = sorted(votes, key=lambda x:votes[x], reverse=True)
    num = min(10, len(sortedKeys))
    topTags = sortedKeys[0:num]
    recall_5 = recall_k(5, topTags, question.tags)
    recall_10 = recall_k(10, topTags, question.tags)
    print recall_5, recall_10
    recall_5_sum += recall_5
    recall_10_sum += recall_10
  print 'Averages'
  print recall_5_sum/len(testSet), recall_10_sum/len(testSet)


testSet = {}
random.seed(2)
for id, question in questions.iteritems():
  if random.random() > 0.999:
    testSet[id] = question






