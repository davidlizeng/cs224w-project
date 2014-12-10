import codecs
import loadData as ld
import json
import nbtext
import tagaffinity
import similarity
import wordvectors
import usergraph

posts_body_file = 'data/posts-body.csv'
posts_bodies = codecs.open(posts_body_file, 'r', 'utf-8')

# Get top tags. Diction of <int, int>: tagID to count in first 50,000 questions
# Only includes tags which appeared more than 50 times.
tcount_infile = open('tcount-50000.txt', 'r')
tempTopTags = json.load(tcount_infile)
tcount_infile.close()
topTags = {}
for idStr, count in tempTopTags.iteritems():
  topTags[int(idStr)] = count

# Dict of question ID (int) to set of tag IDs (ints) which include synonyms
questionTagsSyn = {}
# Dict of question ID (int) to size (int) of question tag list only including popular tags
questionTagsPopOnly = {}

# Multinomial Naive Bayes Model:
mnbd = {}
multiLabelDCache = {}
multiLabelD = {}
# Tag affinity model: precomputed for each fold iteration
tagaff_ttas = {}
tagTermDCache = {}
tagTermD = {}
# Similarity model: precomputed for each fold iteration
sim_model = {}
similarityDCache = {}
similarityD = {}
# Community model: based on user to tag network
usertagnetwork = {}
communityDCache = {}


def setQuestionModelModifications(allQuestions):
  global questionTagsSyn
  global questionTagsPopOnly
  print 'Setting question modifications'
  infile = open('synonyms.txt', 'r')
  tagSyns = {}
  while True:
    s = infile.readline()
    if not s:
      break
    data = set([int(d) for d in s.split()])
    for tid in data:
      assert tid in topTags
      tagSyns[tid] = data
  for qid, question in allQuestions.iteritems():
    currentTags = question.tags
    newTags = set()
    count = 0
    for tid in currentTags:
      newTags.add(tid)
      if tid in tagSyns:
        newTags |= tagSyns[tid]
      if tid in topTags:
        count += 1
    questionTagsSyn[qid] = newTags
    questionTagsPopOnly[qid] = count
  print 'Done with modifications'


def resetModels():
  global tagaff_ttas
  global tagTermDCache
  global mnbd
  global multiLabelDCache
  global sim_model
  global similarityDCache
  global usertagnetwork
  global communityDCache
  tagaff_ttas = {}
  tagTermDCache = {}
  mnbd = {}
  multiLabelDCache = {}
  sim_model = {}
  similarityDCache = {}
  usertagnetwork = {}
  communityDCache = {}


def computeComTagCombineD(alpha, beta, gamma, delta, question, trainQuestions):
  comTagCombineD = {}

  # Tag Term. Stores stuff in cache so we don't have to recompute more than once per question.
  if question.id in tagTermDCache:
    multiLabelD = multiLabelDCache[question.id]
    tagTermD = tagTermDCache[question.id]
    similarityD = similarityDCache[question.id]
    communityD = communityDCache[question.id]
  else:
    posts_bodies.seek(question.bodyByte)
    body = posts_bodies.readline()
    multiLabelD = nbtext.getProbForQuestion(question.id, mnbd, topTags, wordVecs)
    multiLabelDCache[question.id] = multiLabelD
    tagTermD = tagaffinity.getTagTermBasedRankingScores(body, tagaff_ttas, topTags)
    tagTermDCache[question.id] = tagTermD
    similarityD = similarity.getSimilarityRankingScores(question.id, trainQuestions, wordVecs, sim_model, topTags)
    similarityDCache[question.id] = similarityD
    communityD = usergraph.getTagPredictions(question.id, question, usertagnetwork, topTags)
    communityDCache[question.id] = communityD

  for t in topTags:
    comTagCombineD[t] = (alpha * multiLabelD.get(t, 0.0)) + (beta * similarityD.get(t, 0.0)) +\
                        (gamma * tagTermD.get(t, 0.0)) + (delta * communityD.get(t, 0.0))
  return comTagCombineD


# Returns tuple of (scoreAllTags, scorePopularTagsOnly)
def recall_k(k, topTags, actualTags, qid, denominator):
  recall_score = 0.0
  num = min(len(topTags),k)
  for i in xrange(num):
    if topTags[i] in actualTags:
      recall_score += 1.0
  r = recall_score / denominator
  if questionTagsPopOnly[qid] == 0:
    rPop = 0
  else:
    rPop = recall_score / questionTagsPopOnly[qid]
  return (r, rPop)


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
  global tagaff_ttas
  global mnbd
  global sim_model
  global usertagnetwork
  print "Begin Naive Bayes Training"
  mnbd = nbtext.getTagNaiveBayesScores(trainQuestions, topTags, wordToIndex, wordVecs)
  print "Naive Bayes Training Complete"
  print "Begin Tag Affinity Training"
  tagaff_ttas = tagaffinity.getTagTermAffinityScores(trainQuestions, includeCounts=False)
  print "Tag Affinity Training Complete"
  sim_model = similarity.similarityModel(trainQuestions, wordVecs)
  print "Similarity Training Complete"
  usertagnetwork = usergraph.createUserGraph(trainQuestions)
  print "Community Training Complete"


"""
Evaluates the recall@5 and recall@10 scores using the input parameters for each
on the input test data set. Returns the recall@5 score and the recall@10 score.
"""
def comTagCombineModelTest(trainQuestions, testQuestions, outfile=None):
  best_r5_avg, best_r10_avg = 0.0, 0.0
  bestParams5 = [-1.0, -1.0, -1.0, -1.0]
  bestParams10 = [-1.0, -1.0, -1.0, -1.0]
  for alpha in xrange(6):
    alpha = alpha * 0.2
    for beta in xrange(6):
      beta = beta * 0.2
      for gamma in xrange(6):
        gamma = gamma * 0.2
        for delta in xrange(6):
          delta = delta * 0.2

          (r5_sum, r5pop_sum) = (0.0, 0.0)
          (r10_sum, r10pop_sum) = (0.0, 0.0)
          (r5syn_sum, r5synpop_sum) = (0.0, 0.0)
          (r10syn_sum, r10synpop_sum) = (0.0, 0.0)
          for (qid, question) in testQuestions.iteritems():
            comTagCombineD = computeComTagCombineD(alpha, beta, gamma, delta, question, trainQuestions)
            sortedTags = sorted(comTagCombineD, key=lambda x: comTagCombineD[x], reverse=True)
            num = min(10, len(sortedTags))
            topTags = sortedTags[0:num]
            (r5, r5pop) = recall_k(5, topTags, question.tags, qid, len(question.tags))
            (r10, r10pop) = recall_k(10, topTags, question.tags, qid, len(question.tags))
            (r5syn, r5synpop) = recall_k(5, topTags, questionTagsSyn[qid], qid, len(question.tags))
            (r10syn, r10synpop) = recall_k(10, topTags, questionTagsSyn[qid], qid, len(question.tags))
            r5_sum += r5
            r5pop_sum += r5pop
            r5syn_sum += r5syn
            r5synpop_sum += r5synpop
            r10_sum += r10
            r10pop_sum += r10pop
            r10syn_sum += r10syn
            r10synpop_sum += r10synpop

          r5_avg = r5_sum / len(testQuestions)
          r5pop_avg = r5pop_sum / len(testQuestions)
          r5syn_avg = r5syn_sum / len(testQuestions)
          r5synpop_avg = r5synpop_sum / len(testQuestions)
          r10_avg = r10_sum / len(testQuestions)
          r10pop_avg = r10pop_sum / len(testQuestions)
          r10syn_avg = r10syn_sum / len(testQuestions)
          r10synpop_avg = r10synpop_sum / len(testQuestions)
          if r5_avg > best_r5_avg:
            best_r5_avg = r5_avg
            updateParameters(alpha, beta, gamma, delta, bestParams5)
          if r10_avg > best_r10_avg:
            best_r10_avg = r10_avg
            updateParameters(alpha, beta, gamma, delta, bestParams10)
          r5_tuple = (r5_avg, r5pop_avg, r5syn_avg, r5synpop_avg)
          r10_tuple = (r10_avg, r10pop_avg, r10syn_avg, r10synpop_avg)
          print '(%f, %f, %f, %f): r5 = %s, r10 = %s' % (alpha, beta, gamma, delta, r5_tuple, r10_tuple)
          if outfile:
            outfile.write('%f,%f,%f,%f,%s,%s\n' % (alpha, beta, gamma, delta, r5_tuple, r10_tuple))

  return bestParams5, best_r5_avg, bestParams10, best_r10_avg

## Comment out this entire block if not running from Python shell
ld.loadData(True)
# This function must be run. Be careful if this is commented out.
setQuestionModelModifications(ld.questions)
folds = ld.getCVFolds()
print 'Generating word vectors'
frequentWords, wordToIndex = wordvectors.getFrequentWords(ld.questions)
wordVecs = wordvectors.getWordVectors(ld.questions, wordToIndex)
## End block

counter = 0
recall_test_scores = [0.0, 0.0]
for fold in folds[0:5]:
  resetModels()
  counter += 1
  print 'Starting Fold %d' % counter
  trainQuestions = fold[0]
  print 'Fold size %d' % len(fold[0])
  comTagCombineModelTrain(trainQuestions)
  print 'Train complete. Beginning test.'
  testQuestions = fold[1]
  outfile = open('temp/ctc-out_%d.csv' % counter, 'w+')
  params5, score5, params10, score10 = comTagCombineModelTest(trainQuestions, testQuestions, outfile)
  print "Test Values for Run #%d:" % counter
  print "recall@5 params: " + str(params5)
  print "recall@5 score: " + str(score5)
  print "recall@10 params: " + str(params10)
  print "recall@10 score: " + str(score10)
  recall_test_scores[0] += score5
  recall_test_scores[1] += score10
  outfile.close()

print "Average Test Scores:"
print "recall@5 score: " + str(recall_test_scores[0]/10)
print "recall@10 score: " + str(recall_test_scores[1]/10)

posts_bodies.close()
