from random import shuffle
import sys
result = list(map(lambda x:x, open(sys.argv[1], 'r', encoding='utf-8')))
shuffle(result)
with open('pos.txt', 'w') as f:
        for i in result:
                f.write(i)

