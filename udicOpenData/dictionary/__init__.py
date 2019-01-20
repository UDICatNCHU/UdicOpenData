import jieba, os, re
DIR_NAME = os.path.dirname(os.path.abspath(__file__))

def strdecode(sentence):
    if not isinstance(sentence, jieba.text_type):
        try:
            sentence = sentence.decode('utf-8')
        except UnicodeDecodeError:
            sentence = sentence.decode('gbk', 'ignore')
    return sentence.title()


jieba.re_eng = re.compile('[a-zA-Z0-9]', re.I | re.U)
jieba.re_han_default = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&\._% ]+)", re.I | re.U)
jieba.re_userdict = re.compile('^(.+?)(\u0040\u0040[0-9]+)?(\u0040\u0040[a-zA-Z]+)?$', re.I | re.U)
jieba.strdecode = strdecode

jieba.load_userdict(os.path.join(DIR_NAME, 'dict.txt.big.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'ptt.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'wiki.dict.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'attractions.dict.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'dcard.dict.txt'))
jieba.load_userdict(os.path.join(DIR_NAME, 'zh_translate_en.dict'))

# sougou.txt has a bad performance...
# jieba.load_userdict(os.path.join(DIR_NAME, 'sougou.txt'))
