# -*- coding: utf-8 -*-
import requests, json, gc, sys, os.path
from bs4 import BeautifulSoup
from collections import defaultdict
from opencc import OpenCC 

openCC = OpenCC('s2t')
root = '頁面分類'
wikiBaseUrl = 'https://zh.wikipedia.org'

def genUrl(category):
    return 'https://zh.wikipedia.org/wiki/Category:' + category

def dfs(root):
    visited, stack = set(root), [root]
    while stack:
        result = defaultdict(list)
        reverseResult = defaultdict(list)
        
        parent = stack.pop()
        res = BeautifulSoup(requests.get(genUrl(parent)).text)
        # node
        for candidateOffsprings in res.select('.CategoryTreeLabelCategory'):
            tradText = openCC.convert(candidateOffsprings.text).replace('/', '-')

            # if it's a node hasn't been through
            # append these res to stack
            if tradText not in visited:
                visited.add(tradText)
                stack.append(tradText)

                # build dictionary
                result[parent].append(tradText)
                reverseResult[tradText].append(parent)

        if os.path.isfile(parent + '.json'):
            print('skip ' + parent)
            continue
        # 下一頁
        leafNodeList = [res.select('#mw-pages a')]
        while leafNodeList:
            current = leafNodeList.pop(0)

            # notyet 變數的意思是，因為wiki會有兩個下一頁的超連結
            # 頂部跟底部
            # 所以如果把頂部的bs4結果append到leafNodeLIst的話
            # 底部就不用重複加
            notyet = True
            for child in current:
                tradChild = openCC.convert(child.text).replace('/', '-')
                if notyet and tradChild == '下一頁' and child.has_attr('href'):
                    notyet = False
                    leafNodeList.append(BeautifulSoup(requests.get(wikiBaseUrl + child['href']).text).select('#mw-pages a'))
                else:
                    if tradChild != '下一頁' and tradChild != '上一頁':
                        result[parent].append(tradChild)
                        reverseResult[tradChild].append(parent)

        # dump
        json.dump(result, open('{}.json'.format(parent), 'w', encoding='utf-8'))
        json.dump(reverseResult, open('{}.reverse.json'.format(parent), 'w', encoding='utf-8'))
        gc.collect()

dfs(sys.argv[1] if len(sys.argv) else root)