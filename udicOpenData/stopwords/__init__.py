'''
this module supply some segmetation function for multiple language
also remove stopwords as well.
'''
import pickle
from pathlib import Path, PurePath

import nltk
from nltk.stem import WordNetLemmatizer

STOPWORD_PKL = pickle.load(open(str(PurePath(Path(__file__).resolve().parent, 'stopwords.pkl')), 'rb'))
STOPWORD_EN_PKL = pickle.load(open(str(PurePath(Path(__file__).resolve().parent, 'stopwords-en.pkl')), 'rb'))
WORDNET_LEMMATIZER = WordNetLemmatizer()

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('wordnet')

def rmsw(doc, flag=False):
    '''
    parameter:
      doc: input string
      flag: boolean, if true will return segment with pos.
    '''
    import udicOpenData.dictionary
    import jieba.posseg as pseg
    import jieba
    from opencc import OpenCC
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

    cc = OpenCC('tw2s')    # traditional chinese to simplified chinese
    dd = OpenCC('s2tw')    # simplified chinese to traditional chinese  dan 2022/11/21

    # flag means showing part of speech
    if flag:
        return ((dd.convert(i),j) for i,j in pseg.cut(cc.convert(doc))
                if i not in STOPWORD_PKL
                and (is_chinese(i) or (is_english(i) and len(i) >= 2))
                and i not in ['\xa0', '\xc2']
                and not i.isdigit()
                )
    else:
        return (dd.convert(i) for i in jieba.cut(cc.convert(doc))
                if i not in STOPWORD_PKL
                and (is_chinese(i) or (is_english(i) and len(i) >= 2))
                and i not in ['\xa0', '\xc2']
                and not i.isdigit()
                )

# Yang, 2018/08/08
def rmsw_en(doc, flag=False):
    '''
    parameter:
      doc: input string
      flag: boolean, if true will return segment with pos.
    '''
    def has_numbers(input_string):
        return any(char.isdigit() for char in input_string)

    import re
    from nltk import ne_chunk, pos_tag, word_tokenize

    doc = doc.strip()
    chunks = ne_chunk(pos_tag(word_tokenize(doc)))
    words = [w[0] if isinstance(w, tuple) else ' '.join(t[0] for t in w) for w in chunks]
    for word in words:
        word = re.sub(r'[^a-zA-Z0-9 -]', '', word)
        if word and not has_numbers(word) and word.lower() not in STOPWORD_EN_PKL:
            if flag:
                if len(word.split()) > 1:
                    pos = '/'.join([pos_tag(word_tokenize(i))[0][1] for i in word.split()])
                else:
                    pos = pos_tag(word_tokenize(word))
                    if not pos:
                        continue
                    pos = pos[0][1]
                yield WORDNET_LEMMATIZER.lemmatize(word.lower()), pos
            else:
                yield WORDNET_LEMMATIZER.lemmatize(word.lower())
