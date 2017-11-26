# -*- coding: utf-8 -*-
import requests, json, os.path, threading, multiprocessing, pymongo
from bs4 import BeautifulSoup
from collections import defaultdict
from opencc import OpenCC
from random import shuffle

class WikiCategory(object):
    """docstring for WikiCategory"""
    def __init__(self, root=None):
        self.openCC = OpenCC('s2t')
        self.root = root if root else '頁面分類'
        self.wikiBaseUrl = 'https://zh.wikipedia.org'
        self.client = pymongo.MongoClient(None)['nlp']
        self.Collect = self.client['wiki']
        self.reverseCollect = self.client['wikiReverse']
        self.insertNum = 50
        self.queueLock = threading.Lock()
        self.visited, self.stack = set(), []

        if root:
            self.visited, self.stack = set([root]), []
            result, reverseResult = self.dfs(root)
            self.Collect.insert(result)
            self.reverseCollect.insert(reverseResult)
        else:
            f = json.load(open('stack_visited.json', 'r'))
            self.visited, self.stack = set(f['visited']), f['stack']

        workers = [threading.Thread(target=self.thread_dfs, name=str(i)) for i in range(multiprocessing.cpu_count())]

        for thread in workers:
           thread.start()

        # Wait for all threads to complete
        for thread in workers:
            thread.join()

    @staticmethod
    def genUrl(category):
        return 'https://zh.wikipedia.org/wiki/Category:' + category


    def dfs(self, parent):
        result = defaultdict(dict)
        reverseResult = defaultdict(dict)

        res = BeautifulSoup(requests.get(self.genUrl(parent)).text)
        # node
        for candidateOffsprings in res.select('.CategoryTreeLabelCategory'):
            tradText = self.openCC.convert(candidateOffsprings.text).replace('/', '-')

            # if it's a node hasn't been through
            # append these res to stack
            if tradText not in self.visited and '維基人' not in tradText:
                self.visited.add(tradText)
                self.stack.append(tradText)

                # build dictionary
                result[parent].setdefault('node', []).append(tradText)
                reverseResult[tradText].setdefault('parentNode', []).append(parent)

        if self.Collect.find({'key':parent}).limit(1).count():
            self.queueLock.acquire()
            json.dump({'stack':self.stack, 'visited':list(self.visited)}, open('stack_visited.json', 'w', encoding='utf-8'))
            self.queueLock.release()
            return

        # leafNode (要注意wiki的leafNode有下一頁的連結，都要traverse完)
        leafNodeList = [res.select('#mw-pages a')]
        while leafNodeList:
            current = leafNodeList.pop(0)

            # notyet 變數的意思是，因為wiki會有兩個下一頁的超連結
            # 頂部跟底部
            # 所以如果把頂部的bs4結果append到leafNodeLIst的話
            # 底部就不用重複加
            notyet = True
            for child in current:
                tradChild = self.openCC.convert(child.text).replace('/', '-')
                if notyet and tradChild == '下一頁' and child.has_attr('href'):
                    notyet = False
                    leafNodeList.append(BeautifulSoup(requests.get(self.wikiBaseUrl + child['href']).text).select('#mw-pages a'))
                else:
                    if tradChild != '下一頁' and tradChild != '上一頁':
                        result[parent].setdefault('leafNode', []).append(tradChild)
                        reverseResult[tradChild].setdefault('ParentOfLeafNode', []).append(parent)
        # dump
        result = [dict({'key':key}, **value) for key, value in result.items()]
        reverseResult = [dict({'key':key}, **value) for key, value in reverseResult.items()]
        self.queueLock.acquire()
        json.dump({'stack':self.stack, 'visited':list(self.visited)}, open('stack_visited.json', 'w', encoding='utf-8'))
        self.queueLock.release()
        return result, reverseResult

    def thread_dfs(self):
        resultList, reverseResultList = [], []
        while self.stack:
            try:
                self.queueLock.acquire()
                shuffle(self.stack)
                parent = self.stack.pop()
                self.queueLock.release()
                ans = self.dfs(parent)

                # return None，代表這條路以前走過了，應該是爬蟲莫名shutdown
                # 然後從stack_visited.json復原回來時，會發現已經走過的路
                # 但是還是要繼續走下去，只會那些node有些已經存進mongo裡面了
                if ans == None:
                    continue

                result, reverseResult = ans
                resultList.extend(result)
                reverseResultList.extend(reverseResult)

                if len(resultList) > self.insertNum:
                    self.Collect.insert(resultList)
                    resultList = [] # insert完需要重置
                if len(reverseResultList) > self.insertNum:
                    self.reverseCollect.insert(reverseResultList)
                    reverseResultList = [] # insert完需要重置
            except Exception as e:
                self.queueLock.acquire()
                json.dump({'stack':self.stack, 'visited':list(self.visited)}, open('stack_visited.json', 'w', encoding='utf-8'))
                self.stack.append(parent)
                self.queueLock.release()

                self.Collect.insert(resultList)
                self.reverseCollect.insert(reverseResultList)
                raise e
        if resultList:
            self.Collect.insert(resultList)
        if reverseResultList:
            self.reverseCollect.insert(reverseResultList)

    def mergeMongo(self):
        result = defaultdict(dict)
        for term in self.reverseCollect.find({}, {'_id':False}):
            for key, value in term.items():
                if key != 'key':
                    result[term['key']].setdefault(key, []).extend(value)

        result = [dict({'key':key}, **value) for key, value in result.items()]
        self.reverseCollect.remove({})
        self.reverseCollect.insert(result)

if __name__ == '__main__':
    wiki = WikiCategory('日本動畫')
    wiki.mergeMongo()