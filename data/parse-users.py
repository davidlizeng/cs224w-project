#!/usr/bin/python

import xml.etree.ElementTree as ET

INPUT = 'Users.xml'
OUTPUT = 'users.csv'

infile = open(INPUT, 'r')
outfile = open(OUTPUT, 'w+')

# Consume <?xml...> and opening tag lines
# Also consume first "Community" user, which is just a bot
infile.readline()
end = infile.readline().strip()
end = end[:1] + '/' + end[1:]
infile.readline()

lines = 0
outfile.write('## %s\n' % (OUTPUT))
outfile.write('## Id,Reputation,Age,Views,UpVotes,DownVotes,AccountId\n');

# Parse file. Write output to file as we go.
while True:
  s = infile.readline()
  lines += 1
  if s == end:
    break
  data = ET.fromstring(s)
  attr = data.attrib
  outfile.write(
    '%s,%s,%s,%s,%s,%s,%s\n' % (
      attr.get('Id', ''),
      attr.get('Reputation', ''),
      attr.get('Age', ''),
      attr.get('Views', ''),
      attr.get('UpVotes', ''),
      attr.get('DownVotes', ''),
      attr.get('AccountId', '')
    )
  )
  if lines % 10000 == 0:
    print 'Parsed %d lines' % (lines)

infile.close()
outfile.close()
