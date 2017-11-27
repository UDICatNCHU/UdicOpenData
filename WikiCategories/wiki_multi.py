# -*- coding: utf-8 -*-
import requests, json, os.path, threading, multiprocessing, pymongo, logging, sys
from bs4 import BeautifulSoup
from collections import defaultdict
from opencc import OpenCC
from gensim import models


class WikiCategory(object):
    """docstring for WikiCategory"""
    def __init__(self):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, filename='WikiCategory.log')
        self.openCC = OpenCC('s2t')
        self.wikiBaseUrl = 'https://zh.wikipedia.org'
        self.client = pymongo.MongoClient(None)['nlp']
        self.Collect = self.client['wiki']
        self.reverseCollect = self.client['wikiReverse']
        self.queueLock = threading.Lock()
        self.visited, self.stack = set(), []
        self.model = models.KeyedVectors.load_word2vec_format('./med400.model.bin', binary=True)
        self.modelVocab = self.model.wv.vocab
            
    def crawl(self, root=None):
        self.root = root
        if root:
            self.visited, self.stack = set([root]), []
            self.dfs(root)
        else:
            f = json.load(open('stack_visited.json', 'r'))
            self.visited, self.stack = set(f['visited']), f['stack']
        workers = [threading.Thread(target=self.thread_dfs, name=str(i)) for i in range(multiprocessing.cpu_count()*2)]

        for thread in workers:
           thread.start()
        # Wait for all threads to complete
        logging.info('wait for join')
        for thread in workers:
            thread.join()
        logging.info('finish init')

    @staticmethod
    def genUrl(category):
        return 'https://zh.wikipedia.org/wiki/Category:' + category


    def dfs(self, parent):
        logging.info('now is at {}'.format(parent))
        result = defaultdict(dict)
        reverseResult = defaultdict(dict)

        res = requests.get(self.genUrl(parent)).text
        res = BeautifulSoup(res, 'lxml')
        # node
        for candidateOffsprings in res.select('.CategoryTreeLabelCategory'):
            # tradText = self.openCC.convert(candidateOffsprings.text).replace('/', '-')
            tradText = candidateOffsprings.text

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
            logging.info('skip {}'.format(parent))
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
                tradChild = child.text
                if notyet and tradChild == '下一頁' and child.has_attr('href'):
                    notyet = False
                    logging.info(parent)
                    leafNodeList.append(BeautifulSoup(requests.get(self.wikiBaseUrl + child['href']).text, 'lxml').select('#mw-pages a'))
                else:
                    if tradChild not in ['下一頁', '上一頁']:
                        result[parent].setdefault('leafNode', []).append(tradChild)
                        reverseResult[tradChild].setdefault('ParentOfLeafNode', []).append(parent)
        # dump
        result = [dict({'key':key}, **value) for key, value in result.items()]
        reverseResult = [dict({'key':key}, **value) for key, value in reverseResult.items()]
        self.queueLock.acquire()
        json.dump({'stack':self.stack, 'visited':list(self.visited)}, open('stack_visited.json', 'w', encoding='utf-8'))
        self.queueLock.release()
        if result and reverseResult:
            self.Collect.insert(result)
            self.reverseCollect.insert(reverseResult)

    def thread_dfs(self):
        while True:
            try:
                self.queueLock.acquire()
                if self.stack:
                    parent = self.stack.pop()
                    self.queueLock.release()
                else:
                    self.queueLock.release()
                    logging.info("stack is empty!!")
                    break
                self.dfs(parent)
            except Exception as e:
                self.queueLock.acquire()
                json.dump({'stack':self.stack, 'visited':list(self.visited)}, open('stack_visited.json', 'w', encoding='utf-8'))
                self.stack.append(parent)
                self.queueLock.release()
                raise e
        logging.info("finish thread job")                    

    def mergeMongo(self):
        logging.info("merge")
        result = defaultdict(dict)
        for term in self.reverseCollect.find({}, {'_id':False}):
            for key, value in term.items():
                if key != 'key':
                    result[self.openCC.convert(term['key'])].setdefault(key, []).extend([self.openCC.convert(i) for i in value])

        result = [dict({'key':key}, **value) for key, value in result.items()]
        self.reverseCollect.remove({})
        self.reverseCollect.insert(result)
        self.Collect.create_index([("key", pymongo.HASHED)])

        result = defaultdict(dict)
        for term in self.Collect.find({}, {'_id':False}):
            for key, value in term.items():
                if key != 'key':
                    result[self.openCC.convert(term['key'])].setdefault(key, []).extend([self.openCC.convert(i) for i in value])

        result = [dict({'key':key}, **value) for key, value in result.items()]
        self.Collect.remove({})
        self.Collect.insert(result)
        self.reverseCollect.create_index([("key", pymongo.HASHED)])
        logging.info("merge done")

    @staticmethod
    def findPath(keyword):
        Collect = pymongo.MongoClient(None)['nlp']['wikiReverse']
        cursor = list(Collect.find({'key':keyword}).limit(1))[0]
        if 'ParentOfLeafNode' in cursor:
            cursor = cursor['ParentOfLeafNode']
        else:
            cursor = cursor['parentNode']
        queue = {(parent, (keyword, parent)) for parent in set(cursor) - set(keyword)}
        while queue:
            (keyword, path) = queue.pop()
            cursor = Collect.find({'key':keyword}).limit(1)
            if cursor.count():
                parentNodes = list(cursor)[0]
                parentNodes = parentNodes['parentNode']
                for parent in set(parentNodes) - set(path):
                    queue.add((parent, path + (parent, )))
            else:
                yield path

    def findParent(self, keyword):
        candidate = set()
        for path in self.findPath(keyword):
            for parent in path:
                if parent in self.modelVocab and parent != keyword:
                    candidate.add((parent, self.model.similarity(keyword, parent)))
                    break
        return sorted(candidate, key=lambda x:-x[1])


if __name__ == '__main__':
    wiki = WikiCategory()
    # if len(sys.argv) == 2 and sys.argv[1] == 'load':
    #     wiki.crawl()
    #     wiki.mergeMongo()
    # else:
    #     wiki.crawl('日本動畫師')
    #     # wiki.crawl('媒體')
    #     # wiki.crawl('日本電視動畫')
    #     # wiki.crawl('喜欢名侦探柯南的维基人')
    #     # wiki.crawl('日本原創電視動畫')
    #     # wiki.crawl('富士電視台動畫')
    #     # wiki.crawl('萌擬人化')
    #     wiki.mergeMongo()
    # wiki.mergeMongo()
    print(list(wiki.findPath(sys.argv[1])))
    print(list(wiki.findParent(sys.argv[1])))