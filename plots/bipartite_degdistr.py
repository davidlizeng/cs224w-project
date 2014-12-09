import sys
sys.path.append('..')

import bipartite

g = bipartite.getBipartiteGraph('../bipartite_users_tags.txt')
degDistr = {}
for userID, tagsDict in g.iteritems():
  degree = len(tagsDict)
  degDistr[degree] = degDistr.get(degree, 0) + 1

print degDistr

outputTab = open('bipartite_degdistr.tab', 'w+')
for degree, count in degDistr.iteritems():
  outputTab.write('%d %d\n' % (degree, count))
outputTab.close()