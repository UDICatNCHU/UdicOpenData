# Open Sentiment Training Data

自己蒐集的training data、字典和stopwords並且包成package，讓大家不用重複造輪子。

## Usage

安裝：`pip install udicOpenData`

1. 載入實驗室字典, import dictionary
```
from udicOpenData.dictionary import *
```
2. 濾掉stopwords, remove stopwords
p.s. rm stop words時就會跟著載入`1.`實驗室字典了
  ```
  from udicOpenData.stopwords import *

  # default
  rmsw(input string, flag=False)

  # return segmentation with part of speech.
  rmsw(input string, flag=True)
  ```

## For elasticsearch

`dump2es.py` this command will generate two file with different filename extension

please move these two files into elasticsearch plugin folder

1. ik:`dump2es.py ik`
    * stopword:`ext_stopword.dic`
    * dictionary:`mydict.dic`
    ```json
    巨蛋
    遠雄
    趙藤雄
    蔡英文
    陳水扁
    立法院
    蔡正元
    頂新
    食安
    柯p
    ...
    ...
    ...
    ```
2. jieba:`dump2es.py jieba`
    * stopword:`ext_stopword.txt`
    * dictionary:`mydict.dict`
    ```json
    巨蛋 99
    遠雄 99
    趙藤雄 99
    蔡英文 99
    陳水扁 99
    立法院 99
    蔡正元 99
    頂新 99
    食安 99
    柯p 99
    ...
    ...
    ...
    ```

stopword:
```json
上 
上來 
上去 
將不 
為
www 
http 
https 
.com 
– 
● 
○ 
～ 
...
...
...
```


## 所有語料大小：

* 正面情緒：約有309163筆，44M
* 負面情緒：約有320456筆，15M

## 訓練好的Model：

1. 政治版Model：
  * 成份：
    以下資料皆濾掉標題包含 `[公告]` 的文章
    * `pos.txt` 正面情緒的model，將下列版的內容做shuffle，包含：  
      * adulation版：標題 + 內文
      * dreams-wish版：標題 + 內文
      * happy版：標題 + 內文
      * kindness版：標題 + 內文裡面的`好人行為`區段的文字
      * luchky版：標題
    * `neg.txt` 負面情緒的model，包含：  
      * HatePolitics版：標題 + 內文（只有包含黑特且不包含RE的才納入）
  * 大小：
    * pos.txt：13222筆
    * neg.txt：13222筆

## 產生出資料給 `Swinger`

`python text2json.py positive的檔名(文檔，以一句一句為單位) positive.json（為output檔案的檔名） True/False(若為True就代表要把stopword濾掉
)`：會自動把一行一行的語料，斷詞段好給Swinger當input data
