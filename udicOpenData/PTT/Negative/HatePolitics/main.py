import json, sys

topic = sys.argv[2]
title_file = open(topic+'.title.txt', 'w', encoding='utf-8')
content_file = open(topic+'.content.txt', 'w', encoding='utf-8')

for i in json.load(open(sys.argv[1], 'r', encoding='utf-8'))['articles']:
	if i.get('article_title', '')!=None and '[黑特]' in i.get('article_title', '') and 'R' not in i.get('article_title', ''):
		title_file.write(i.get('article_title', '').replace('\n', '') + '\n')
		content_file.write(i.get('content', '').replace('\n', '') + '\n')