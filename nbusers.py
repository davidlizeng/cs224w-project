import operator
import numpy as np
from sklearn.naive_bayes import BernoulliNB as bnb
import loadData

numQuestions = 50000

tagCountDict = {}
for tag in loadData.tags:
  tagCountDict[tag] = loadData.tags[tag].count
sortedTags = sorted(tagCountDict.items(), key=operator.itemgetter(1), reverse=True)

nbuserDict = {}
nbuserId = 0

for qid in loadData.questions:
  if not loadData.questions[qid].userId in nbuserDict:
    nbuserDict[loadData.questions[qid].userId] = nbuserId
    nbuserId += 1
  for aid in loadData.questions[qid].answers:
    if not loadData.answers[aid].userId in nbuserDict:
      nbuserDict[loadData.answers[aid].userId] = nbuserId
      nbuserId += 1
      
X = np.zeros((numQuestions/5, nbuserId))
y = np.zeros(numQuestions/5)
yvalues = np.array([0, 1])
for t in range(0,10):
  tag = sortedTags[t][0]
  print loadData.tags[tag].tag
  clf = bnb(alpha=0.001)
  i = 0
  for qid in loadData.questions:
    i = i % (numQuestions/5)
    X[i][nbuserDict[loadData.questions[qid].userId]] = 1
    for aid in loadData.questions[qid].answers:
      X[i][nbuserDict[loadData.answers[aid].userId]] = 1
    if tag in loadData.questions[qid].tags:
      y[i] = 1
    else:
      y[i] = 0
    if i == numQuestions/5 - 1:
      clf.partial_fit(X,y, classes=yvalues)
    i += 1

  clf.fit(X,y)
  print "Fit Complete"

  falseNegatives = 0
  totalNegatives = 0
  falsePositives = 0
  totalPositives = 0
  for i in range(0,numQuestions/5):
    if y[i] == 1:
      totalPositives += 1
      if clf.predict(X[i]) != 1:
        falseNegatives += 1
    if y[i] == 0:
      totalNegatives += 1
      if clf.predict(X[i]) != 0:
        falsePositives += 1
  print "False Negatives: " + str(falseNegatives) + ", " + str(totalPositives) + ", " + str((falseNegatives*1.0) / max(1,totalPositives))
  print "False Positives: " + str(falsePositives) + ", " + str(totalNegatives) + ", " + str((falsePositives*1.0) / max(1,totalNegatives))

  
