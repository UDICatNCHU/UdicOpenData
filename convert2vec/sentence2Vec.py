# -*- coding: utf-8 -*-
import json, sys, csv
from gensim import models
import numpy as np
model = models.KeyedVectors.load_word2vec_format('med400.model.bin', binary=True)
raw = json.load(open(sys.argv[1], 'r'))

inputvec = []
for i in raw:
	sum = np.zeros(400)
	for j in i:
		try:
			sum = np.add(sum, model[j])
		except Exception as e:
			pass
	inputvec.append([sys.argv[2]] + sum.tolist())
# export as csv
with open(sys.argv[3],"w") as f:
	w = csv.writer(f)
	w.writerows(inputvec)