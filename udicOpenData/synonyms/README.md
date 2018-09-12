# How to get synonym dictionary from Wiki

1. Install dependencies:
    `pip3 install opencc-python-reimplemented`

2. Import Wiki dump: 

    ```bash
    mysql test < zhwiki-latest-page.sql;
    mysql test < zhwiki-latest-redirect.sql;
    ```
3. Join with table Page on page_id:

    ```bash
    mysql -e "
        SELECT p.page_id,
               p.page_title SOURCE,
                            r.rd_title sanitized
        FROM redirect r
        INNER JOIN page p ON r.rd_from = p.page_id
        WHERE r.rd_namespace=0
          OR r.rd_namespace=14;
    " test > synonym.txt
    ```
4. Filter out some useless synonym (e.q. 四月二日 -> 4月2日、台灣 -> 臺灣):

    ```python
        from opencc import OpenCC
        import json, re
        openCC = OpenCC('s2t')
        result = []
        for line in open('synonym.txt','r'):
            if '台灣' in line:
                continue
            elif all(
                    character in '0123456789年月日\t\n '
                    for character in line
                ):
                # delete something like 09月22日 -> 9月22日.
                continue
            else:
                source, target = openCC.convert(line).strip().split('\t')
                if source == target:
                    # means line[0] and line[1] was traditional and simplified chinese
                    # after translation done by opencc, they're now the same.
                    continue
                else:
                    result.append((source, target))


        json.dump(result[1:], open('synonym.json', 'w'))
    ```
