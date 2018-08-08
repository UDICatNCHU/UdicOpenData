import json
import os

import nltk

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
STOPWORD_JSON = json.load(open(os.path.join(DIR_NAME, 'stopwords.json'), 'r', encoding='utf-8'))
STOPWORD_JSON_EN = json.load(open(os.path.join(DIR_NAME, 'stopwords-en.json'), 'r',\
 encoding='utf-8'))
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

def rmsw(doc, flag=False):
    '''
    parameter:
      flag: boolean, if true will return segment with pos.
    '''
    import udicOpenData.dictionary
    import jieba.posseg as pseg
    import jieba
    def is_chinese(keyword):
        for uchar in keyword:
            if '\u4e00' <= uchar <= '\u9fff':
                continue
            else:
                return False
        return True

    def is_english(keyword):
        if not is_chinese(keyword) and keyword.isalpha():
            return True
        return False

    doc = doc.strip()

    # flag means showing part of speech
    if flag:
        return (tuple(i) for i in pseg.cut(doc)
                if i.word not in STOPWORD_JSON
                and (is_chinese(i.word) or (is_english(i.word) and len(i.word) >= 2))
                and i.word not in ['\xa0', '\xc2']
                and not i.word.isdigit()
                )
    else:
        return (i for i in jieba.cut(doc)
                if i not in STOPWORD_JSON
                and (is_chinese(i) or (is_english(i) and len(i) >= 2))
                and i not in ['\xa0', '\xc2']
                and not i.isdigit()
                )

# Yang, 2018/07/06
def rmsw_en(doc, flag=False):
    def has_numbers(input_string):
        return any(char.isdigit() for char in input_string)

    import re
    from nltk import ne_chunk, pos_tag, word_tokenize

    chunks = ne_chunk(pos_tag(word_tokenize(doc)))
    words = [w[0] if isinstance(w, tuple) else ' '.join(t[0] for t in w) for w in chunks]
    for word in words:
        word = re.sub(r'[^a-zA-Z0-9 -]', '', word)
        if word and not has_numbers(word) and word.lower() not in STOPWORD_JSON_EN:
            yield word
