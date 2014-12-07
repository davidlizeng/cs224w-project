#!/usr/bin/python

import xml.etree.ElementTree as ET
import codecs

INPUT = 'Posts.xml'
OUTPUT_META = 'posts-meta.csv'
OUTPUT_TITLE = 'posts-title.csv'
OUTPUT_BODY = 'posts-body.csv'
OUTPUT_TAGS = 'posts-tags.csv'

infile = open(INPUT, 'r')
outfile_meta = codecs.open(OUTPUT_META, 'w', 'utf-8')
outfile_title = codecs.open(OUTPUT_TITLE, 'w', 'utf-8')
outfile_body = codecs.open(OUTPUT_BODY, 'w', 'utf-8')
outfile_tags = codecs.open(OUTPUT_TAGS, 'w', 'utf-8')

# Consume <?xml...> and opening tag lines
infile.readline()
end = infile.readline().strip()
end = end[:1] + '/' + end[1:]

lines = 0
outfile_meta.write('## %s\n' % (OUTPUT_META))
outfile_meta.write('## Id,PostTypeId,ParentId,AcceptedAnswerId,CreationDate,Score,ViewCount,OwnerUserId,AnswerCount,CommentCount\n');
outfile_title.write('## %s\n' % (OUTPUT_TITLE))
outfile_title.write('## Id,Title\n');
outfile_body.write('## %s\n' % (OUTPUT_BODY))
outfile_body.write('## Id,Body\n');
outfile_tags.write('## %s\n' % (OUTPUT_TAGS))
outfile_tags.write('## Id,Tags\n');

# Parse file. Write output to file as we go.
while True:
  s = infile.readline()
  lines += 1
  if s == end:
    break
  data = ET.fromstring(s)
  attr = data.attrib

  outfile_meta.write(
    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
      attr.get('Id', ''),
      attr.get('PostTypeId', ''),
      attr.get('ParentId', ''),
      attr.get('AcceptedAnswerId', ''),
      attr.get('CreationDate', ''),
      attr.get('Score', ''),
      attr.get('ViewCount', ''),
      attr.get('OwnerUserId', ''),
      attr.get('AnswerCount', ''),
      attr.get('CommentCount', ''),
    )
  )
  outfile_title.write(
    '%s,%s\n' % (
      attr.get('Id', ''),
      attr.get('Title', '').replace('\n', ' ').replace('\r', ' '),
    )
  )
  outfile_body.write(
    '%s,%s\n' % (
      attr.get('Id', ''),
      attr.get('Body', '').replace('\n', ' ').replace('\r', ' '),
    )
  )
  outfile_tags.write(
    '%s,%s\n' % (
      attr.get('Id', ''),
      attr.get('Tags', ''),
    )
  )
  if lines % 10000 == 0:
    print 'Parsed %d lines' % (lines)

infile.close()
outfile_meta.close()
outfile_title.close()
outfile_body.close()
outfile_tags.close()
