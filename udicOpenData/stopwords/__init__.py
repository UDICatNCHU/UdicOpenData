import json, os
DIR_NAME = os.path.dirname(os.path.abspath(__file__))

STOPWORD_JSON = json.load(open(os.path.join(DIR_NAME, 'stopwords.json'), 'r'))