import json, sys, random
with open(sys.argv[2], 'w', encoding='utf-8') as f:
	j = json.load(open(sys.argv[1], 'r', encoding='utf-8'))
	random.shuffle(j['articles'])
	for i in j['articles']:
		if i.get('article_title', '')!=None and '[公告]' not in i.get('article_title', '') and 'Re' not in i.get('article_title', ''):
			if len(i.get('article_title', '')) >= 9:
				f.write(i.get('article_title', '').replace('\n', '') + '\n')
			f.write(i.get('content', '').replace('\n', '') + '\n')