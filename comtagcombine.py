import codecs
import loadData
import json
import tagaffinity

posts_body_file = 'data/posts-body.csv'
posts_bodies = codecs.open(posts_body_file, 'r', 'utf-8')

# Get top tags. Diction of <int, int>: tagID to count in first 50,000 questions
# Only includes tags which appeared more than 50 times.
tcount_infile = open('tcount-50000.txt', 'r')
tempTopTags = json.load(tcount_infile)
tcount_infile.close()
topTags = {}
for idStr, count in tempTopTags.items():
  topTags[int(idStr)] = count


# Get rid of these once api is established
multiLabelD = {}
simRankD ={}
communityD = {}
# Tag affinity model: precomputed for each fold iteration
tagaff_ttas = {}
tagTermDCache = {}


def resetModels():
  tagaff_ttas = {}
  tagTermDCache = {}


def computeComTagCombineD(alpha, beta, gamma, delta, question):
  comTagCombineD = {}

  # Tag Term. Stores stuff in cache so we don't have to recompute more than once per question.
  if question.id in tagTermDCache:
    tagTermD = tagTermDCache[question.id]
  else:
    posts_bodies.seek(question.bodyByte)
    body = posts_bodies.readline()
    tagTermD = tagaffinity.getTagTermBasedRankingScores(body, tagaff_ttas, topTags)
    tagTermDCache[question.id] = tagTermD

  for t in topTags:
    comTagCombineD[t] = (alpha * multiLabelD[t]) + (beta * simRankD[t]) +\
                        (gamma * tagTermD[t]) + (delta * communityD[t])
  return comTagCombineD


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
  # Tag affinity precomputation
  tagaff_ttas = tagaffinity.getTagTermAffinityScores(trainQuestions, includeCounts=False)


"""
Evaluates the recall@5 and recall@10 scores using the input parameters for each
on the input test data set. Returns the recall@5 score and the recall@10 score.
"""
def comTagCombineModelTest(testQuestions):
  best_recall_5_avg, best_recall_10_avg = 0.0, 0.0
  bestParams5 = [-1.0, -1.0, -1.0, -1.0]
  bestParams10 = [-1.0, -1.0, -1.0, -1.0]
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
          for (qid, question) in testQuestions.items():
            comTagCombineD = computeComTagCombineD(alpha, beta, gamma, delta, question)
            sortedTags = sorted(comTagCombineD, key=lambda x: comTagCombineD[x], reverse=True)
            num = min(10, len(sortedTags))
            topTags = sortedTags[0:num]
            recall_5 = recall_k(5, topTags, question.tags)
            recall_10 = recall_k(10, topTags, question.tags)
            recall_5_sum += recall_5
            recall_10_sum += recall_10

          recall_5_avg = recall_5_sum / len(testQuestions)
          recall_10_avg = recall_10_sum / len(testQuestions)
          if recall_5_avg > best_recall_5_avg:
            best_recall_5_avg = recall_5_avg
            updateParameters(alpha, beta, gamma, delta, bestParams5)
          if recall_10_avg > best_recall_10_avg:
            best_recall_10_avg = recall_10_avg
            updateParameters(alpha, beta, gamma, delta, bestParams10)

  return bestParams5, best_recall_5_avg, bestParams10, best_recall_10_avg


counter = 0
recall_test_scores = [0.0, 0.0]
for fold in folds:
  resetModels()
  counter += 1
  trainQuestions = fold[0]
  comTagCombineModelTrain(trainQuestions)
  testQuestions = fold[1]
  params5, score5, params10, score10 = comTagCombineModelTest(testQuestions)
  print "Test Values for Run #%d:" % counter
  print "recall@5 params: " + str(params5)
  print "recall@5 score: " + str(score5)
  print "recall@10 params: " + str(params10)
  print "recall@10 score: " + str(score10)
  recall_test_scores[0] += score5
  recall_test_scores[1] += score10

print "Average Test Scores:"
print "recall@5 score: " + str(recall_test_scores[0]/10)
print "recall@10 score: " + str(recall_test_scores[1]/10)

posts_bodies.close()




