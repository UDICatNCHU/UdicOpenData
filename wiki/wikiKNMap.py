import jieba.posseg as pseg
import random, json, jieba, os, sys
from itertools import *

stopwords = json.load(open('stopwrds/stopwords.json', 'r'))
jieba.load_userdict(os.path.join('dictionary', 'dict.txt.big.txt'))
jieba.load_userdict(os.path.join("dictionary", "NameDict_Ch_v2"))
remaining_list = ['。','，',':',';','(',')','[',']','《','》','〈','〉','（','）','「','」','它','是','為','系','或','簡稱','的','以','指', '是指','別稱','又稱','全稱','綽號','一']

data = json.load(open(sys.argv[1], 'r'))

length = []
endIndex = []
result = []
for entity, value in data.items():
	tmp = {}
	key, value = list(value.items())[0]

	# calculate max len of sentence
	length.append(key.index(value)+len(value))

	aftersplit = key.split(entity)
	tmp['key'] = [pseg.lcut(k) for k in aftersplit]
	remain_index = [(upperIndex, index) for upperIndex, subarr in enumerate(tmp['key']) for index, word in enumerate(subarr) if word.word in remaining_list]
	tmp_cut_key = pseg.lcut(key)

	tmp['start'] = 0
	for i in range(len(tmp_cut_key)):
		if value not in ''.join(map(lambda x:x.word, tmp_cut_key[i:])): 
			tmp['start'] = i-1
			break

	tmp['end'] = 0
	for i in reversed(range(len(tmp_cut_key))):
		if value not in ''.join(map(lambda x:x.word, tmp_cut_key[:i+1])): 
			tmp['end'] = i+2
			break
	# calculate max endIndex, which is an important imput for lstm.
	endIndex.append(tmp['end'])

	if value != ''.join(map(lambda x:x.word, tmp_cut_key[tmp['start']:tmp['end']])):
		print(value, '-------------', ''.join(map(lambda x:x.word, tmp_cut_key[tmp['start']:tmp['end']])))
		raise "error"
	tmp_arr = []
	for upperIndex, subarr in enumerate(tmp['key']):
		tmp_subarr = []
		for index, pair in enumerate(subarr):
			if (upperIndex, index) in remain_index:
				tmp_subarr.append(pair.word)
			else:
				tmp_subarr.append(pair.flag)
		tmp_arr.append(tmp_subarr)

	tmp_for_tmp_arr = []
	for index, i in enumerate(tmp_arr):
		tmp_for_tmp_arr.append(i)
		if index != 4:
			tmp_for_tmp_arr.append(['entity'])

	tmp_arr = list(chain(*tmp_for_tmp_arr))

	tmp['key'] = tmp_arr
	tmp['raw'] = key
	tmp['start_normalize'] = tmp['start'] / len(tmp['key'])
	tmp['end_normalize'] = tmp['end'] / len(tmp['key'])
	print(tmp, tmp['start_normalize'], tmp['end_normalize'])
	result.append(tmp)

json.dump(result, open(sys.argv[2], 'w'))
print("min length of characters need to be at least: {}".format(str(max(length))))
print("min length of lstm input need to be at least: {}".format(str(max(endIndex))))