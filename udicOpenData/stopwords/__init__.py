from udicOpenData.dictionary import *
import json, os, re
DIR_NAME = os.path.dirname(os.path.abspath(__file__))

STOPWORD_JSON = json.load(open(os.path.join(DIR_NAME, 'stopwords.json'), 'r'))

def rmsw(doc):
    def is_not_number(s):
        try:
            float(s)
            return False
        except ValueError:
            return True
    doc = re.sub(r"[http|www]\S+", "", doc)
    doc = doc.strip()
    return [i for i in jieba.cut(doc) if i not in STOPWORD_JSON and is_not_number(i) and i not in ['\xa0', '\xc2']]