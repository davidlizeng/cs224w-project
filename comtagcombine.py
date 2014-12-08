import loadData
import json

tcount_infile = open('tcount-50000.txt', 'r')
topTagsStrInt = json.load(tcount_infile)
tcount_infile.close()

topTagsIntInt = {}
for idStr, count in topTagsStrInt.items():
  topTagsIntInt[int(idStr)] = count

# Get rid of these once api is established
multiLabelD = {}
simRankD ={}
tagTermD = {}
communityD = {}
comTagCombineD = {}

def computeComTagCombineD(alpha, beta, gamma, delta, question):
  comTagCombineD = {}
  for t in topTagsIntInt.tags:
    comTagCombineD[t] = alpha*multiLabelD[t] + beta*simRankD[t] + gamma*tagTermD[t] + delta*communityD[t]

def recall_k(k, topTags, actualTags):
  recall_score = 0.0
  num = min(len(topTags),k)
  for i in xrange(num):
    if topTags[i] in actualTags:
      recall_score += 1.0
  return recall_score / len(actualTags)

def updateParameters(alpha, beta, gamma, delta, bestParams):
  bestParams[0] = alpha
  bestParams[1] = beta
  bestParams[2] = gamma
  bestParams[3] = delta

"""
Takes in a training set of questions and trains alpha, beta, gamma, delta for
recall@5 and recall@10. Returns the best params for recall@5 and recall@10 and
the corresponding parameters
"""
def comTagCombineModelTrain(trainQuestions):
  best_recall_5_avg, best_recall_10_avg = 0.0, 0.0
  bestParams5 = [-1, -1, -1, -1]
  bestParams10 = [-1, -1, -1, -1]
  for alpha in xrange(11):
    alpha = alpha * 0.1
    for beta in range(0,11):
      beta = beta * 0.1
      for gamma in xrange(11):
        gamma = gamma * 0.1
        for delta in xrange(11):
          delta = delta * 0.1

          recall_5_sum = 0.0
          recall_10_sum = 0.0
          for question in trainQuestions:
            computeComTagCombineD(alpha, beta, gamma, delta, question)
            sortedTags = sorted(comTagCombineD, key=lambda x: comTagCombineD[x], reverse=True)
            num = min(10, len(sortedTags))
            topTags = sortedTags[0:num]
            recall_5 = recall_k(5, topTags, question.tags)
            recall_10 = recall_k(10, topTags, question.tags)
            recall_5_sum += recall_5
            recall_10_sum += recall_10

          recall_5_avg = recall_5_sum / len(trainQuestions)
          recall_10_avg = recall_10_sum / len(trainQuestions)
          if recall_5_avg > best_recall_5_avg:
            best_recall_5_avg = recall_5_avg
            updateParameters(alpha, beta, gamma, delta, bestParams5)
          if recall_10_avg > best_recall_10_avg:
            best_recall_10_avg = recall_10_avg
            updateParameters(alpha, beta, gamma, delta, bestParams10)

  return bestParams5, best_recall_5_avg, bestParams10, best_recall_10_avg

"""
Evaluates the recall@5 and recall@10 scores using the input parameters for each
on the input test data set. Returns the recall@5 score and the recall@10 score.
"""
def comTagCombineModelTest(testQuestions, params5, params10):
  recall_5_sum, recall_10_sum = 0.0, 0.0

  for question in testQuestions:
    computeComTagCombineD(params5[0], params5[1], params5[2], params5[3], question)
    sortedTags = sorted(comTagCombineD, key=lambda x: comTagCombineD[x], reverse=True)
    num = min(5, len(sortedTags))
    recall_5 = recall_k(5, topTags, question.tags)
    recall_5_sum += recall_5

  for question in testQuestions:
    computeComTagCombineD(params10[0], params10[1], params10[2], params10[3], question)
    sortedTags = sorted(comTagCombineD, key=lambda x: comTagCombineD[x], reverse=True)
    num = min(10, len(sortedTags))
    recall_10 = recall_k(10, topTags, question.tags)
    recall_10_sum += recall_10

  return recall_5_sum / len(testQuestions), recall_10_sum / len(testQuestions)




bestVals5, best_recall_5, bestVals10, best_recall_10 = comTagCombineModel(trainQuestions)
print "Training Values:"
print "recall@5 params: " + str(bestVals5)
print "recall@5 score: " + str(best_recall_5)
print "recall@10 params: " + str(bestVals10)
print "recall@10 score: " + str(best_recall_10)
recall_5_test, recall_10_test = comTagCombineModelTest(testQuestions, params5, params10)
print "Test Values"
print "recal@5 score: " + str(recall_5_test)
print "recall@10 score: " + str(recall_10_test)





