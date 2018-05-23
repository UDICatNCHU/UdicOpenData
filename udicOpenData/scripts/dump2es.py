import os, json
for dictfile in os.listdir('../dictionary'):
	if '.txt' in dictfile:
		with open('../dictionary/' + dictfile, 'r', encoding='utf-8') as f:
			new_dictionary = [' '.join('_'.join(keyword.split()[:-1]).rsplit('_', 1))+'\n' for keyword in f]
		with open('{}.dict'.format(dictfile.replace('.txt', '')), 'w', encoding='utf-8') as f:
			for keyword in new_dictionary:
				f.write(keyword)

with open('stopword.txt', 'w') as f:
	for i in ' \n'.join(json.load(open('../stopwords/stopwords.json'))):
		f.write(i)