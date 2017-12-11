import jieba, json, sys, os
import jieba.posseg as pseg
stopwords = json.load(open('stopwords.json', 'r'))
jieba.load_userdict(os.path.join('dictionary', 'dict.txt.big.txt'))
jieba.load_userdict(os.path.join("dictionary", "NameDict_Ch_v2"))

def removeStopWords(key_and_value, rmstop=sys.argv[3]):
	def condition(x):
		x = list(x)
		word, flag = x[0], x[1]
		if len(word) > 1 and flag!='eng' and flag != 'm' and flag !='mq' and word not in stopwords:
			return True
		return False

	key, value = key_and_value
	if rmstop == 'True':
		key = filter(condition, pseg.cut(key))
		key = list(map(lambda x:list(x)[0], key))
		value = filter(condition, pseg.cut(value))
		value = list(map(lambda x:list(x)[0], value))
	else:
		key = jieba.lcut(key)
		value = jieba.lcut(value.replace('\n', '').strip())
	return {'key':key, 'value':value}

with open(sys.argv[1], 'r') as f:
	f = json.load(f)
	result = list(map(removeStopWords, f.items()))

with open(sys.argv[2], 'w') as f:
	json.dump(result, f)