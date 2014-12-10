import re

(AVG, POP, SIM, SIMPOP) = (0, 1, 2, 3)
(ALPHA, BETA, GAMMA, DELTA) = (0, 1, 2, 3)

def tuple4ToStr(t):
  return '(%.3f,%.3f,%.3f,%.3f)' % (t[0], t[1], t[2], t[3])

def parseOutputLine(line):
  return re.split(r',\(|\),\(|\)|, |,', line)[:-1]

def getMap():
  infile = open('../output_ntc.txt', 'r')
  m = {}
  while True:
    s = infile.readline()
    if not s:
      break
    data = parseOutputLine(s)
    params = (float(data[0]), float(data[1]), float(data[2]), float(data[3]))
    r5s = (float(data[4]), float(data[5]), float(data[6]), float(data[7]))
    r10s = (float(data[8]), float(data[9]), float(data[10]), float(data[11]))
    m[params] = (r5s, r10s)
  infile.close()
  return m

def getBestForIndex(m, index):
  (best5, b5p) = (0.0, (0.0, 0.0, 0.0, 0.0))
  (best10, b10p) = (0.0, (0.0, 0.0, 0.0, 0.0))
  for params, (score5, score10) in m.iteritems():
    if score5[index] > best5:
      (best5, b5p) = (score5[index], params)
    if score10[index] > best10:
      (best10, b10p) = (score10[index], params)
  return ((best5, b5p), (best10, b10p))

# Recall@5 avg tc (.6, .6, .8, .0)
# Recall@5 avg ntc (.4, .4, 1.0, .6)
def outputGraph(m, index):
  outfile = open('ntc_output.tab', 'w+')
  for var in xrange(6):
    v = round(var * 0.2, 1)
    t = (.4, .4, 1.0, v)
    (score5, score10) = m[t]
    outfile.write('%f %f\n' % (v, score5[index]))
  outfile.close()

m = getMap()
outputGraph(m, AVG)
print '   AVG', getBestForIndex(m, AVG)
print '   POP', getBestForIndex(m, POP)
print '   SIM', getBestForIndex(m, SIM)
print 'SIMPOP', getBestForIndex(m, SIMPOP)
