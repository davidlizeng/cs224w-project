#!/usr/bin/python

import xml.etree.ElementTree as ET
import codecs

INPUT = 'Comments.xml'
OUTPUT_META = 'comments-meta.csv'
OUTPUT_TEXT = 'comments-text.csv'

infile = open(INPUT, 'r')
outfile_meta = codecs.open(OUTPUT_META, 'w', 'utf-8')
outfile_text = codecs.open(OUTPUT_TEXT, 'w', 'utf-8')

# Consume <?xml...> and opening tag lines
infile.readline()
end = infile.readline().strip()
end = end[:1] + '/' + end[1:]

lines = 0
outfile_meta.write('## %s\n' % (OUTPUT_META))
outfile_meta.write('## Id,PostId,Score,CreationDate,UserId\n');
outfile_text.write('## %s\n' % (OUTPUT_TEXT))
outfile_text.write('## Id,Text\n');

# Parse file. Write output to file as we go.
while True:
  s = infile.readline()
  lines += 1
  if s == end:
    break
  data = ET.fromstring(s)
  attr = data.attrib

  outfile_meta.write(
    '%s,%s,%s,%s,%s\n' % (
      attr.get('Id', ''),
      attr.get('PostId', ''),
      attr.get('Score', ''),
      attr.get('CreationDate', ''),
      attr.get('UserId', ''),
    )
  )
  outfile_text.write(
    '%s,%s\n' % (
      attr.get('Id', ''),
      attr.get('Text', '').replace('\n', ' ').replace('\r', ' '),
    )
  )
  if lines % 10000 == 0:
    print 'Parsed %d lines' % (lines)

infile.close()
outfile_meta.close()
outfile_text.close()
