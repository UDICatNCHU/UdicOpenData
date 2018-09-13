# How to get ambiguous words from Wiki

1. Install dependencies:
    `pip3 install opencc-python-reimplemented`

2. Import Wiki dump: 

    ```bash
    mysql test < zhwiki-latest-page.sql;
    mysql test < zhwiki-latest-categorylinks.sql;
    ```
3. Run script:
    `python3 ambiguous.py`
4. Result:
    ```json
    [
      "三从",
      "三位一體_(消歧義)",
      "三体_(消歧义)",
      "三佛寺",
      "三俁山",
      "三個世界",
      "三個願望",
      "三元",
      "三元乡",
      "三元塔",
      "三元宮",
      "三元里",
      "三元镇",
      "三光",
      "三光村_(消歧義)",
      "三八",
      "三公_(消歧义)",
      "三公二",
      "三六九棋",
      "三兴镇",
      "三农县_(消歧义)",
      "三冠",
      ...
    ]
    ```