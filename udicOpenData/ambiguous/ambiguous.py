'''
This script would dump all ambiguous word into ambiguation.json
'''
import json

import pymysql

CONNECTION = pymysql.connect(host='db',
                             user='root',
                             password='',
                             db='test',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
with CONNECTION:
    CURSOR = CONNECTION.cursor()
    CURSOR.execute("select cl_from from categorylinks where cl_to='消歧义';")

    # 一字消歧異、二字消歧異等等
    CATEGORY_IDS = [item['cl_from'] for item in CURSOR.fetchall()]
    CATEGORY_TITLE_QUERY = "select page_title from page where page_id IN ({});".format(
        str(CATEGORY_IDS)[1:-1])
    CURSOR.execute(CATEGORY_TITLE_QUERY)

    # 所有屬於一字消歧異、二字消歧異的頁面的title
    CATEGORY_TITLE = [title['page_title'].decode(
        'utf-8') for title in CURSOR.fetchall()]
    AMBIGUOUS_PAGE_ID_QUERY = "select cl_from from categorylinks where cl_to IN ({});".format(
        str(CATEGORY_TITLE)[1:-1])
    CURSOR.execute(AMBIGUOUS_PAGE_ID_QUERY)

    # 所有消歧異頁面的page_id
    AMBIGUOUS_PAGE_ID = [page_id['cl_from'] for page_id in CURSOR.fetchall()]
    AMBIGUOUS_PAGE_TITLE_QUERY = "select page_title from page where page_id IN ({})".format(
        str(AMBIGUOUS_PAGE_ID)[1:-1])
    CURSOR.execute(AMBIGUOUS_PAGE_TITLE_QUERY)

    # 所有消歧異頁面的title
    AMBIGUOUS_PAGE_TITLE = [p['page_title'].decode(
        'utf-8') for p in CURSOR.fetchall()]
    json.dump(AMBIGUOUS_PAGE_TITLE, open('ambiguation.json', 'w'))
