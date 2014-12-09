import json
import loadData as ld

## Loads data. Can comment out.
# ld.loadData(answersComments=True)
# s = ld.getUsersSubset(ld.users, ld.questions, ld.answers, ld.comments)
# g = getGraph(ld.users, ld.questions, ld.answers, ld.comments)

output_file = 'bipartite_users_tags.txt'

BIPARTITE_QUESTION_SCORE = 1.0
BIPARTITE_ANSWER_SCORE = 0.7
BIPARTITE_COMMENT_SCORE = 0.1

# User id to dictionary of (int tagID) : (float score)
# If passing in a subset (trainQuestions), still include ALL answers and comments
def getGraph(users, trainQuestions, answers, comments):
  graph = {}

  counter = 0
  for userID in s.keys():
    d = {}
    user = users[userID]
    for qid in user.questions:
      question = questions.get(qid, None)
      if question:
        for tid in question.tags:
          d[tid] = d.get(tid, 0.0) + BIPARTITE_QUESTION_SCORE
    for aid in user.answers:
      question = questions.get(answers[aid].questionId, None)
      if question:
        for tid in question.tags:
          d[tid] = d.get(tid, 0.0) + BIPARTITE_ANSWER_SCORE
    for cid in user.comments:
      postID = comments[cid].postId
      if postID in questions:
        question = questions.get(postID, None)
        if question:
          for tid in question.tags:
            d[tid] = d.get(tid, 0.0) + BIPARTITE_COMMENT_SCORE
      else:
        question = questions.get(answers[postID].questionId, None)
        if question:
          for tid in question.tags:
            d[tid] = d.get(tid, 0.0) + BIPARTITE_COMMENT_SCORE
    graph[userID] = d
    counter += 1
    if counter % 5000 == 0:
      print 'Done %d' % counter

  return graph

def outputGraph(g):
  outfile = open(output_file, 'w+')
  outfile.write(json.dumps(g, separators=(',',':')))
  outfile.close()

def getBipartiteGraph(filename = output_file):
  infile = open(filename, 'r')
  g_temp = json.load(infile)
  infile.close()
  g = {}
  for userID_str, d_temp in g_temp.iteritems():
    d = {}
    for tagID_str, score in d_temp.iteritems():
      d[int(tagID_str)] = score
    g[int(userID_str)] = d
  return g

