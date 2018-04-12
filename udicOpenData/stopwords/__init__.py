from udicOpenData.dictionary import *
import jieba.posseg as pseg
import json, os, re
DIR_NAME = os.path.dirname(os.path.abspath(__file__))

STOPWORD_JSON = json.load(open(os.path.join(DIR_NAME, 'stopwords.json'), 'r'))

def rmsw(doc, flag=False):
    '''
    parameter:
      flag: boolean, if true will return segment with pos.
    '''
    def is_chinese(keyword):
        for uchar in keyword:
            if '\u4e00' <= uchar<='\u9fff':
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
            and i.word.isdigit() == False 
        )
    else:
        return (i for i in jieba.cut(doc)
            if i not in STOPWORD_JSON 
            and (is_chinese(i) or (is_english(i) and len(i) >= 2)) 
            and i not in ['\xa0', '\xc2']
            and i.isdigit() == False 
        )