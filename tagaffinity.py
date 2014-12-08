#!/usr/bin/python

import codecs
import json
import loadData as ld
import operator
import wordvectors

posts_body_file = 'data/posts-body.csv'

# Top-level dictionary is term : dict
# Inner dictionary is tagID : # times in same post
# To get Aff(tag, term):
#    Look up term in top-dictionary to get dict
#    If term does not exist, then not a frequent term, skip
#    If term exists, then get dict value
#    Look up tagID in dict.
#    If exists, then get score. Otherwise 0.
# Returns tagCounts as well. Map from tagID : # posts it appeared. Only if >= 50
def getTagTermAffinityScores(questions, includeCounts=True):
  frequentWords = set(wordvectors.getFrequentWords(questions)[0])
  ttas = {}
  tagCounts = {}
  infile_body = codecs.open(posts_body_file, 'r', 'utf-8')
  for (qid, question) in questions.items():
    for tagID in question.tags:
      tagCounts[tagID] = tagCounts.get(tagID, 0) + 1
    infile_body.seek(question.bodyByte)
    postWords = wordvectors.getWordsFromPost(infile_body.readline())
    for word in set(postWords):
      if word not in frequentWords:
        continue
      inner_dict = ttas.get(word, {})
      for tagID in question.tags:
        inner_dict[tagID] = inner_dict.get(tagID, 0) + 1
      ttas[word] = inner_dict
  infile_body.close()

  for (term, inner_dict) in ttas.items():
    for (tagID, freq) in inner_dict.items():
      inner_dict[tagID] = float(freq) / tagCounts[tagID]

  if includeCounts:
    finalTagCounts = {}
    for (tagID, count) in tagCounts.items():
      if count >= 50:
        finalTagCounts[tagID] = count
    return (ttas, finalTagCounts)
  else:
    return ttas

# Utility function
# Given question body and ttas, tagCounts from getTagTermAffinityScores,
# will compute ranking score for EVERY tag in tagCounts for the questionBody
# Returns dict of tagID : score
def getTagTermBasedRankingScores(questionBody, ttas, tagCounts):
  postWords = wordvectors.getWordsFromPost(questionBody)
  result = {}
  for tagID in tagCounts.keys():
    result[tagID] = 1.0
  for word in postWords:
    if word in ttas:
      inner_dict = ttas[word]
      for (tagID, score) in result.items():
        result[tagID] *= (1 - inner_dict.get(tagID, 0))
  for (tagID, score) in result.items():
    result[tagID] = 1 - score
  return result

# Calculates recall@k score
def recall_K(k, topTags, actualTags):
  recall_score = 0.0
  for i in xrange(k):
    if int(topTags[i][0]) in actualTags:
      recall_score += 1.0
  return recall_score / len(actualTags)

# Returns recall@5 and recall@10 scores for a question
def getRecallScores(questionBody, correctTags, ttas, tagCounts):
  ttbrs = getTagTermBasedRankingScores(questionBody, ttas, tagCounts)
  s_ttbrs = sorted(ttbrs.items(), key=operator.itemgetter(1), reverse=True)
  recall5 = recall_K(5, s_ttbrs, correctTags)
  recall10 = recall_K(10, s_ttbrs, correctTags)
  return (recall5, recall10)

# Returns recall@5 and recall@10 scores for numTest
def runTagAffinity(numTrain, numTest):
  ld.loadUsers()
  ld.loadTags()
  ld.loadQuestions(numTrain, True, numTest)
  # (ttas, finalTagCounts) = getTagTermAffinityScores(questions)
  ttas_file = codecs.open('ttas-50000.txt', 'r', 'utf-8')
  tc_file = codecs.open('tcount-50000.txt', 'r', 'utf-8')
  ttas = json.load(ttas_file)
  finalTagCounts = json.load(tc_file)
  ttas_file.close()
  tc_file.close()

  posts_bodies = codecs.open(posts_body_file, 'r', 'utf-8')
  (sum5, sum10) = (0.0, 0.0)
  numTest = len(ld.questions)
  counter = 0
  for qid, q in ld.questions_test.items():
    posts_bodies.seek(q.bodyByte)
    body = posts_bodies.readline()
    (recall5, recall10) = getRecallScores(body, q.tags, ttas, finalTagCounts)
    sum5 += recall5
    sum10 += recall10
    counter += 1
    if counter % 100 == 0:
      print 'Done %d' % counter
    # print 'Q #%d: %f %f' % (qid, recall5, recall10)
  return (sum5 / numTest, sum10 / numTest)

(recall5, recall10) = runTagAffinity(50000, 10000)
print ' recall@5: %f' % recall5
print 'recall@10: %f' % recall10
