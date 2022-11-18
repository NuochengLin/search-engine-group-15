import shelve
from nltk.stem.snowball import SnowballStemmer
import re, math
import os
from numpy import array
query = input("Please enter your query: ")
pattern = re.compile(r"[a-zA-Z0-9]+")
stemmer = SnowballStemmer("english")
q = stemmer.stem(query.split()[0])
print(q)
l = len(query.split())
print(l)
with shelve.open(os.path.join("./index/record2" , 'inverted_index'), flag='c', writeback=True) as index:
    with shelve.open(os.path.join("./index/record2", 'id_url'), flag='c') as mapping:
        length = 0
        token_list = []
        for t in pattern.finditer(query):
            word = stemmer.stem(t.group(0))
            token_list.append(word)
            length += index[word]["idf"] ** 2
        length = math.sqrt(length)
        heap = []
        v = array()
        for d in mapping:
            contain = 0
            score = 0
            for term in pattern.finditer(query):
                word = stemmer.stem(term.group(0))
                if d in index[word]:
                    contain += 1
                    v.append(index[word][d]["freq"] * index[word]["idf"] / length)
            ratio = contain/l
            if ratio >= 0.75:
                heapq.heappush(heap, (-ratio,d))
        for i in heap[:10]:
            print(i, end = "\n")
