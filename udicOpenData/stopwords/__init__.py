from udicOpenData.dictionary import *
import jieba.posseg as pseg
import json, os, re
DIR_NAME = os.path.dirname(os.path.abspath(__file__))

STOPWORD_JSON = json.load(open(os.path.join(DIR_NAME, 'stopwords.json'), 'r'))

def rmsw(doc, flag=None):
    def is_chinese(keyword):
        for uchar in keyword:
            if '\u4e00' <= uchar<='\u9fff':
                continue
            else:
                return False
        return True
    doc = re.sub(r"[http|www]\S+", "", doc)
    doc = doc.strip()
    if flag:
        return (i.word for i in pseg.cut(doc) if i.flag.startswith(flag) and i.word not in STOPWORD_JSON and is_chinese(i.word) and i.word not in ['\xa0', '\xc2'])
    else:
        return (i for i in jieba.cut(doc) if i not in STOPWORD_JSON and is_chinese(i) and i not in ['\xa0', '\xc2'])