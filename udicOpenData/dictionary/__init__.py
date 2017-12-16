import jieba, os
DIR_NAME = os.path.dirname(os.path.abspath(__file__))

jieba.load_userdict(os.path.join(DIR_NAME, 'dict.txt.big.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, '鄉民擴充辭典.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'wiki.dict.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'attractions.dict.txt'))
