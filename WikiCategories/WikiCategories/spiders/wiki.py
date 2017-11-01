# -*- coding: utf-8 -*-
import scrapy, requests, json
from bs4 import BeautifulSoup
from WikiCategories.items import WikicategoriesItem
from collections import defaultdict
from opencc import OpenCC
openCC = OpenCC('s2t')

def genUrl(domain, i):
    return 'http://' + domain + i['href']

class WikiSpider(scrapy.Spider):
    name = 'wiki'
    allowed_domains = ['zh.wikipedia.org']
    root = 'https://zh.wikipedia.org/wiki/Category:各国动画师'

    start_urls = []
    for i in BeautifulSoup(requests.get(root).text).select('.CategoryTreeLabelCategory'):
        if i.has_attr('href') and 'Category' in i['href']:
            start_urls.append(genUrl(allowed_domains[0], i))

    def parse(self, response):
        res = BeautifulSoup(response.body)
        result = defaultdict(list)
        reverseResult = defaultdict(list)
        root = openCC.convert(res.select('#firstHeading')[0].text.split(':')[-1])
        visited, queue = set(root), [(res, root)]
        while queue:
            res, parent = queue.pop(0)
            # node
            for candidateOffsprings in res.select('.CategoryTreeLabelCategory'):
                # if it's a node hasn't been through
                # append to queue
                tradText = openCC.convert(candidateOffsprings.text)
                if tradText not in visited:
                    visited.add(tradText)
                    # append these res to queue
                    queue.append((BeautifulSoup(requests.get(genUrl(self.allowed_domains[0], candidateOffsprings)).text), tradText))

                    # build dictionary
                    result[parent].append(tradText)
                    reverseResult[tradText].append(parent)

            # 下一頁
            leafNodeList = [res.select('#mw-pages a')]
            while leafNodeList:
                current = leafNodeList.pop(0)
                notyet = True
                for child in current:
                    tradChild = openCC.convert(child.text)
                    if notyet and tradChild == '下一頁':
                        notyet = False
                        leafNodeList.append(BeautifulSoup(requests.get(genUrl(self.allowed_domains[0], child)).text).select('#mw-pages a'))
                    else: 
                        if tradChild != '下一頁' and tradChild != '上一頁':
                            result[parent].append(tradChild)
                            reverseResult[tradChild].append(parent)

        json.dump(result, open('{}.json'.format(root), 'w', encoding='utf-8'))
        json.dump(reverseResult, open('{}.reverse.json'.format(root), 'w', encoding='utf-8'))