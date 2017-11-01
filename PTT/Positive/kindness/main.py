import json, sys, re
with open(sys.argv[2], 'w', encoding='utf-8') as f:
	for i in json.load(open(sys.argv[1], 'r', encoding='utf-8'))['articles']:
		if i.get('article_title', '')!=None and '[公告]' not in i.get('article_title', '') :
			f.write(i.get('article_title', '').replace('\n', '') + '\n')

			content = re.search(r'好人行為]：(.+?)\ \[對於這種行為您', i.get('content', '').replace('\n', ''))
			if content != None:
				f.write(re.search(r'好人行為]：(.+?)\ \[對於這種行為您', i.get('content', '').replace('\n', '')).group(1) + '\n')
