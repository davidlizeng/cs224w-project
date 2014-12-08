import codecs
import numpy as np

comments_meta_file = 'data/comments-meta-marked.csv'
comments_text_file = 'data/comments-text.csv'
posts_meta_file = 'data/posts-meta-marked.csv'
posts_body_file = 'data/posts-body.csv'
posts_title_file = 'data/posts-title.csv'
posts_tags_file = 'data/posts-tags.csv'
users_file = 'data/users.csv'
tags_file = 'data/tags.csv'

users = {}
tags = {}
questions = {}
answers = {}
comments = {}


class User:
  def __init__(self, id, rep, views, up, down):
    self.id = id
    self.rep = rep
    self.views = views
    self.up = up
    self.down = down
    self.questions = []
    self.answers = []
    self.comments = []

class Tag:
  def __init__(self, id, tag, count):
    self.id = id
    self.tag = tag
    self.count = count

class Question:
  def __init__(self, id, bestAnswerId, date, score, views, userId, titleByte, tagsByte, bodyByte):
    self.id = id
    self.bestAnswerId = bestAnswerId
    self.date = date
    self.score = score
    self.views = views
    self.userId = userId
    self.titleByte = titleByte
    self.tagsByte = tagsByte
    self.bodyByte = bodyByte
    self.answers = []
    self.comments = []
    self.tags = []

class Answer:
  def __init__(self, id, questionId, date, score, userId, bodyByte):
    self.id = id
    self.questionId = questionId
    self.date = date
    self.score = score
    self.userId = userId
    self.bodyByte = bodyByte
    self.comments = []

class Comment:
  def __init__(self, id, postId, score, date, userId, textByte):
    self.id = id
    self.postId = postId
    self.score = score
    self.data = date
    self.userId = userId
    self.textByte = textByte

def loadUsers():
  print "Loading Users"
  lines = open(users_file, 'r')
  lines.readline()
  lines.readline()
  while True:
    line = lines.readline()
    if line == '':
      break
    vals = line.rstrip('\n').split(',')
    id = int(vals[0])
    rep = int(vals[1])
    views = int(vals[3])
    up = int(vals[4])
    down = int(vals[5])
    users[id] = User(id, rep, views, up, down)
  lines.close()
  print "Loading Users Complete"

def loadTags():
  print "Loading Tags"
  lines = open(tags_file, 'r')
  lines.readline()
  lines.readline()
  while True:
    line = lines.readline()
    if line == '':
      break
    vals = line.rstrip('\n').split(',')
    id = int(vals[0])
    tag = vals[1]
    count = int(vals[2])
    tags[id] = Tag(id, tag, count)
  lines.close()
  print "Loading Tags Complete"

def loadQuestions(num, getTags = True):
  print "Loading Questions"
  lines = open(posts_meta_file, 'r')
  lines.readline()
  lines.readline()
  count = 0
  if getTags:
    tag_file = codecs.open(posts_tags_file, 'r')
    revMap = {}
    for id in tags:
      revMap[tags[id].tag] = id

  while count < num:
    line = lines.readline()
    if line == '':
      break
    vals = line.rstrip('\n').split(',')

    type = int(vals[1])
    if type != 1:
      continue
    if vals[7] == '':
      continue
    userId = int(vals[7])
    if userId not in users:
      continue

    id = int(vals[0])
    date = vals[4]
    score = int(vals[5])
    views = int(vals[6])
    titleByte = int(vals[10])
    tagsByte = int(vals[11])
    bodyByte = int(vals[12])
    if vals[3] != '':
      bestAnswerId = int(vals[3])
    else:
      bestAnswerId = None
    questions[id] = Question(id, bestAnswerId, date, score, views, userId, titleByte, tagsByte, bodyByte)
    if getTags:
      tag_file.seek(tagsByte)
      tag_list = tag_file.readline().replace('<', ' ').replace('>', ' ').split()
      for tag in tag_list:
        if tag in revMap:
          questions[id].tags.append(revMap[tag])
    users[userId].questions.append(id)
    count += 1

  if getTags:
    tag_file.close()
  lines.close()
  print "Loading Questions Complete"


def loadAnswers():
  print "Loading Answers"
  lines = open(posts_meta_file)
  lines.readline()
  lines.readline()
  while True:
    line = lines.readline()
    if line == '':
      break
    vals = line.rstrip('\n').split(',')
    type = int(vals[1])
    if type != 2:
      continue
    questionId = int(vals[2])
    if questionId not in questions:
      continue
    if vals[7] == '':
      continue
    userId = int(vals[7])
    if userId not in users:
      continue

    id = int(vals[0])
    date = vals[4]
    score = int(vals[5])
    bodyByte = int(vals[12])
    answers[id] = Answer(id, questionId, date, score, userId, bodyByte)
    questions[questionId].answers.append(id)
    users[userId].answers.append(id)
  lines.close()
  print "Loading Answers Complete"

def loadComments():
  print "Loading Comments"
  lines = open(comments_meta_file)
  lines.readline()
  lines.readline()
  while True:
    line = lines.readline()
    if line == '':
      break
    vals = line.rstrip('\n').split(',')
    postId = int(vals[1])
    table = None
    if postId in questions:
      table = questions
    elif postId in answers:
      table = answers
    if table == None:
      continue
    if vals[4] == '':
      continue
    userId = int(vals[4])
    if userId not in users:
      continue
    id = int(vals[0])
    score = int(vals[2])
    date = vals[3]
    textByte = int(vals[4])
    comments[id] = Comment(id, postId, score, date, userId, textByte)
    table[postId].comments.append(id)
    users[userId].comments.append(id)

  lines.close()
  print "Loading Comments Complete"


def loadData():
  loadUsers()
  loadTags()
  loadQuestions(50000, True)
  # loadAnswers()
  # loadComments()

def getCVFolds():
  folds = []
  k = 10
  num_questions = len(questions)
  fold_size = num_questions/k
  ids = questions.keys()
  np.random.seed(0)
  np.random.shuffle(ids)
  for i in xrange(k):
    folds.append(({}, {}))
    for j in xrange(num_questions):
      if j >= i * fold_size and j < (i + 1) * fold_size:
        folds[i][1][ids[j]] = questions[ids[j]]
      else:
        folds[i][0][ids[j]] = questions[ids[j]]
  return folds







