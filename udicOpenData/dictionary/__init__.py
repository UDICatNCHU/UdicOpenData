import jieba, os
DIR_NAME = os.path.dirname(os.path.abspath(__file__))

jieba.load_userdict(os.path.join(DIR_NAME, 'dict.txt.big.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'ptt.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'wiki.dict.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'attractions.dict.txt'))
# sougou.txt has a bad performance...
# jieba.load_userdict(os.path.join(DIR_NAME, 'sougou.txt'))