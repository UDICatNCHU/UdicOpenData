import pyspark
import jieba, json, sys, os
import jieba.posseg as pseg
conf = pyspark.SparkConf().setAll([('spark.driver.memory', '30g'), ('spark.driver.host', '172.17.0.21'), ('spark.app.id', 'local-1492693477461'), ('spark.rdd.compress', 'True'), ('spark.serializer.objectStreamReset', '100'), ('spark.master', 'local[*]'), ('spark.executor.id', 'driver'), ('spark.submit.deployMode', 'client'), ('spark.driver.port', '39274'), ('spark.app.name', 'PySparkShell')])
sc = pyspark.SparkContext(conf=conf)
stopwords = json.load(open('stopwords.json', 'r'))
jieba.load_userdict(os.path.join('dictionary', 'dict.txt.big.txt'))
jieba.load_userdict(os.path.join("dictionary", "NameDict_Ch_v2"))

def removeStopWords(sentence, rmstop=sys.argv[3]):
	def condition(x):
		x = list(x)
		word, flag = x[0], x[1]
		if len(word) > 1 and flag!='eng' and flag != 'm' and flag !='mq' and word not in stopwords:
			return True
		return False
	if rmstop == 'True':
		result = filter(condition, pseg.cut(sentence))
	else:
		result = pseg.cut(sentence)
	result = map(lambda x:list(x)[0], result)
	return list(result)

t = sc.textFile(sys.argv[1], 20)
result = t.map(removeStopWords).collect()

with open(sys.argv[2], 'w') as f:
	json.dump(result, f)