# -*- coding: utf-8 -*-
import requests, json, sys, os.path, threading, multiprocessing, pymongo
from bs4 import BeautifulSoup
from collections import defaultdict
from opencc import OpenCC
from random import shuffle

openCC = OpenCC('s2t')
root = sys.argv[1] if len(sys.argv) == 2 else '頁面分類'
wikiBaseUrl = 'https://zh.wikipedia.org'

client = pymongo.MongoClient(None)['nlp']
Collect = client['wiki']
reverseCollect = client['wikiReverse']

intsertNum = 50
queueLock = threading.Lock()

def genUrl(category):
    return 'https://zh.wikipedia.org/wiki/Category:' + category


def dfs(parent):
    result = defaultdict(list)
    reverseResult = defaultdict(list)

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

    if Collect.find({'key':parent}).limit(1).count():
        print('skip ' + parent)
        queueLock.acquire()
        json.dump({'stack':stack, 'visited':list(visited)}, open('stack_visited.json', 'w', encoding='utf-8'))
        queueLock.release()
        return
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
    result = [{'key':key, 'value':list(set(value))} for key, value in result.items()]
    reverseResult = [{'key':key, 'value':list(set(value))} for key, value in reverseResult.items()]
    queueLock.acquire()
    json.dump({'stack':stack, 'visited':list(visited)}, open('stack_visited.json', 'w', encoding='utf-8'))
    queueLock.release()
    return result, reverseResult

def thread_dfs():
    resultList, reverseResultList = [], []
    while stack:
        try:
            queueLock.acquire()
            shuffle(stack)
            parent = stack.pop()
            queueLock.release()
            ans = dfs(parent)
            if ans == None:
                continue

            result, reverseResult = ans
            resultList.extend(result)
            reverseResultList.extend(reverseResult)

            if len(resultList) > intsertNum:
                Collect.insert(resultList)
                print('insert resultList')
                resultList = [] # insert完需要重置
            if len(reverseResultList) > intsertNum:
                reverseCollect.insert(reverseResultList)
                print('insert reverseResultList')
                reverseResultList = [] # insert完需要重置
        except Exception as e:
            queueLock.acquire()
            json.dump({'stack':stack, 'visited':list(visited)}, open('stack_visited.json', 'w', encoding='utf-8'))
            queueLock.release()
            print('==============================')
            print(parent)
            print(str(e))
            print(stack)
            print('==============================')
            stack.append(parent)
            print(stack)
            raise e

if __name__ == '__main__':
    if os.path.isfile('stack_visited.json'):
        print('load stack_visited.json')
        f = json.load(open('stack_visited.json', 'r'))
        visited, stack = set(f['visited']), f['stack']
    else:
        visited, stack = set(root), [root]
        dfs(root)

    workers = [threading.Thread(target=thread_dfs, name=str(i)) for i in range(1)]

    for thread in workers:
       thread.start()

    # Wait for all threads to complete
    for thread in workers:
        thread.join()

    print('finished!!!')
