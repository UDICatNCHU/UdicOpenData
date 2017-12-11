# Open Sentiment Training Data

有鑑於Training Data實在太難找了，所以乾脆自己做一個然後公開  
期望大家都能夠共享自己的Training Data  
讓 Sentiment Analysis 能更進一步~

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