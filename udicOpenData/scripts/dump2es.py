#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, pkg_resources, sys
__name__ = 'udicOpenData'
mode = sys.argv[1]
dictionary_filename_extension = 'dic' if mode == 'ik' else 'dict'
stopword_filename_extension = 'dic' if mode == 'ik' else 'txt'

# -2 is index of array, means doesn't need weight
# -1 means containing weight
dictionary_pattern = -2 if mode == 'ik' else -1
filepath = pkg_resources.resource_filename(__name__, 'dictionary')

# output dictionary for elasticsearch
with open('mydict.{}'.format(dictionary_filename_extension), 'w', encoding='utf-8') as outputFile:
	for dictfile in os.listdir(pkg_resources.resource_filename(__name__, 'dictionary')):
		if '.txt' in dictfile:
			with open(os.path.join(filepath, dictfile), 'r', encoding='utf-8') as f:
				print(dictfile)
				new_dictionary = [' '.join('_'.join(keyword.split()[:dictionary_pattern]).rsplit('_', 1))+'\n' for keyword in f]

			# output to output file
			for keyword in new_dictionary:
				outputFile.write(keyword)

# output stopword for elasticsearch
with open('ext_stopword.{}'.format(stopword_filename_extension), 'w') as f:
	for i in ' \n'.join(json.load(open(pkg_resources.resource_filename(__name__, 'stopwords/stopwords.json'), 'r'))):
		f.write(i)