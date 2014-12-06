import re
import math
from utilities import Stemmer
from collections import defaultdict
from sets import Set


#for the purposes of this class,
#we'll consider each of titles and abstracts to be individual documents
#for purposes of idf
class tf_idf(object):
    def __init__(self):
        self.stem = True
        self.stopWords = loadStopWords("stopwords.txt", self.stem)

    def store_tf_idf(self, loader, allPapers=False, stem=True):
        print "Computing Inverse Document Frequency"

        if not stem:
            self.stem = stem
            self.stopWords = loadStopWords("stopwords.txt", stem)

        self.computeIdf(loader)

        print "Storing User Tf-Idf Vectors"
        self.storeUserVectors(loader)
        print "Storing Paper Tf-Idf Vectors"
        self.storePaperVectors(loader, allPapers)

    def computeIdf(self, loader, addlText=[]):
        #document frequency statistics
        self.df = defaultdict(lambda: 1)
        self.n = 1  # smooth by adding a document that contains every word

        for id, paper in loader.papers.iteritems():
            self.addInstances(paper.title)
            self.addInstances(paper.abstract)

        for id, paper in loader.pastPapers.iteritems():
            self.addInstances(paper.title)

        for text in addlText:
            self.addInstances(text)

        s = math.log(self.n)
        self.idf = defaultdict(lambda: s)

        for word, count in self.df.iteritems():
            self.idf[word] -= math.log(count)

    def addInstances(self, doc):
        if len(doc) > 1:
            self.n += 1

            tokens = set(getTokens(doc, self.stem))
            for token in tokens:
                self.df[token] += 1

    def computeSimilarity(self, objectOne, objectTwo, jaccard=False):

        intersection = intersect(objectOne.tfList, objectTwo.tfList)

        if jaccard:
            intersectionSize = len(intersection)
            unionSize =\
                len(objectOne.tfList) + len(objectTwo.tfList) - intersectionSize

            return intersectionSize * 1.0 / unionSize

        else:
            sum = 0.0
            for token in intersection:
                sum += objectOne.tfVector[token] \
                    * objectTwo.tfVector[token]

            return sum

    def storeUserVectors(self, loader):

        for id, user in loader.users.iteritems():
            textList = []

            for paper in user.papers:
                textList.append(paper.title)
                textList.append(paper.abstract)
            for paper in user.pastPapers:
                textList.append(paper.title)
                textList.append(paper.abstract)

            user.tfVector, user.tfList = self.getVector(textList)

    def storePaperVectors(self, loader, allPapers):

        for id, paper in loader.papers.iteritems():
            textList = []
            textList.append(paper.title)
            textList.append(paper.abstract)

            paper.tfVector, paper.tfList = self.getVector(textList)

        if allPapers:
            for id, paper in loader.pastPapers.iteritems():
                textList = []
                textList.append(paper.title)
                textList.append(paper.abstract)

                paper.tfVector, paper.tfList = self.getVector(textList)

    def getVector(self, textList):
        counts = defaultdict(lambda: 0)
        tfList = []

        for text in textList:
            for token in getTokens(text, self.stem):
                if not token in self.stopWords:
                    counts[token] += 1

        sumSq = 0
        for token in counts:
            counts[token] *= self.idf[token]
            sumSq += counts[token] ** 2

        length = math.sqrt(sumSq)
        for token in counts:
            counts[token] /= length
            tfList.append(token)

        tfList.sort()
        return counts, tfList


stemmer = Stemmer.Stemmer("english")


def getTokens(doc, stem):
    tokens = (re.sub('[^\w\s]', ' ', doc))\
        .lower()\
        .split()

    if stem:
        return stemmer.stemWords(tokens)
    else:
        return tokens


def loadStopWords(file, stem):
    stopWords = Set()
    file = open('feature_extraction/'+file)
    for line in file:
        line = line[:-1]
        if stem:
            stopWords.add(stemmer.stemWord(line))
        else:
            stopWords.add(line)

    return stopWords


def intersect(list1, list2):
    i = 0
    j = 0

    intersection = []

    len1 = len(list1)
    len2 = len(list2)

    while i < len1 and j < len2:
        if list1[i] == list2[j]:
            intersection.append(list1[i])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1

    return intersection
