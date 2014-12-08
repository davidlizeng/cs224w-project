import re
import math
import snowballstemmer
from collections import defaultdict
import numpy as np
import codecs

stemmer = snowballstemmer.stemmer('english');
stopwords_file = 'stopwords.txt'
posts_body_file = 'data/posts-body.csv'

def loadStopWords(file):
  stopWords = set()
  infile = open(file, 'r')
  for line in infile:
    word = line.strip()
    stopWords.add(stemmer.stemWord(word))
  return stopWords

def getWordsFromPost(post):
  words = re.sub('[^\w\s]', ' ', re.sub('<[^<]+?>', ' ', post)).lower().split()
  return stemmer.stemWords(words)

def getWordFrequencies(questions, stopWords):
  infile = codecs.open(posts_body_file, 'r', 'utf-8')
  freqs = defaultdict(int)
  for id, question in questions.iteritems():
    infile.seek(question.bodyByte)
    body = infile.readline()
    words = set(getWordsFromPost(body))
    for word in words:
      if not (word.isdigit() or (word in stopWords)):
        freqs[word] += 1
  infile.close()
  return freqs

def countFrequentWords(freqs):
  words = []
  wordToIndex = {}
  index = 0
  for (key, val) in freqs.items():
    if val >= 20:
      words.append(key)
      wordToIndex[key] = index
      index += 1
  return (words, wordToIndex)

def getWordVector(words, wordToIndex):
  vector = np.zeros(len(wordToIndex))
  for w in words:
    if w in wordToIndex:
      vector[wordToIndex[w]] += 1
  return vector

def getWordVectors(questions, wordToIndex):
  infile = codecs.open(posts_body_file, 'r', 'utf-8')
  wordVecs = {}
  for id, question in questions.iteritems():
    infile.seek(question.bodyByte)
    body = infile.readline()
    postWords = getWordsFromPost(body)
    vector = getWordVector(postWords, wordToIndex)
    wordVecs[id] = vector
  infile.close()
  return wordVecs

def getFrequentWords(questions):
  stopWords = loadStopWords(stopwords_file)
  freqs = getWordFrequencies(questions, stopWords)
  words, wordToIndex = countFrequentWords(freqs)
  return (words, wordToIndex)

# words, wordToIndex = getFrequentWords(questions)
# wordVecs = getWordVectors(questions, wordToIndex)
