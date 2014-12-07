#!/usr/bin/python

import xml.etree.ElementTree as ET

INPUT = 'PostLinks.xml'
OUTPUT = 'postlinks.csv'

infile = open(INPUT, 'r')
outfile = open(OUTPUT, 'w+')

# Consume <?xml...> and opening tag lines
infile.readline()
end = infile.readline().strip()
end = end[:1] + '/' + end[1:]

lines = 0
outfile.write('## %s\n' % (OUTPUT))
outfile.write('## Id,CreationDate,PostId,RelatedPostId,LinkTypeId\n');

# Parse file. Write output to file as we go.
while True:
  s = infile.readline()
  lines += 1
  if s == end:
    break
  data = ET.fromstring(s)
  attr = data.attrib
  outfile.write(
    '%s,%s,%s,%s,%s\n' % (
      attr.get('Id', ''),
      attr.get('CreationDate', ''),
      attr.get('PostId', ''),
      attr.get('RelatedPostId', ''),
      attr.get('LinkTypeId', ''),
    )
  )
  if lines % 10000 == 0:
    print 'Parsed %d lines' % (lines)

infile.close()
outfile.close()
