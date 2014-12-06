#!/usr/bin/python

import codecs
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
def getTagTermAffinityScores(questions):
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

  finalTagCounts = {}
  for (tagID, count) in tagCounts.items():
    if count >= 50:
      finalTagCounts[tagID] = count

  return (ttas, finalTagCounts)

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


