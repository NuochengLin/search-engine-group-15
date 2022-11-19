import shelve
from nltk.stem.snowball import SnowballStemmer
import re, math
import os
import heapq
import time


# def intersect(*postings):
#     if len(postings) <= 1:
#         return postings[0]
#     else:
#         result = []
#         a = iter(postings[0])
#         b = iter(postings[1])
#         if not (a and b):
#             print("fail")
#             return []
#         a1 = a.__next__()
#         b1 = b.__next__()
#         while a1 and b1:
#             if a1 > b1:
#                 b1 = next(b, None)
#             elif a1 < b1:
#                 a1 = next(a, None)
#             else:
#                 result.append(a1)
#                 a1 = next(a, None)
#                 b1 = next(b, None)
#         return intersect(*([result] + list(postings[2:])))

def ranking_query(query, index, mapping):
    token_list = set()
    candidate = set()
    for word in query:
        if word in index and index[word]["idf"] > 0.2:
            for d in index[word]:
                if d != "idf":
                    candidate.add(d)
            token_list.add(word)
    # bool_result = intersect(*sorted(token_list, key= lambda x:len(x)))
    # print(bool_result)
    heap = []
    for d in candidate:
        contain = 0
        score = 0
        for term in token_list:
            contain += 1
            if d in index[term]:
                score += index[term][d]["w"] * index[term]["idf"]
        if contain / len(token_list) >= 0.75:
            heapq.heappush(heap, (-score, d))
    for score, id in heap[:5]:
        print(id, ": ", mapping[id], "with score: ", -score, end="\n")


if __name__ == "__main__":
    with shelve.open(os.path.join("./index", 'inverted_index'), flag='c', writeback=True) as index:
        with shelve.open(os.path.join("./index", 'id_url'), flag='c') as mapping:
            pattern = re.compile(r"[a-zA-Z0-9]+")
            stemmer = SnowballStemmer("english")
            query_list = ["cristina lopes", "machine learning", "ACM", "master of software engineering"]
            for query in query_list:
                print("----------------------------------")
                print("start processing query", query, ": ")
                token_list = []

                s = time.time()
                for t in pattern.finditer(query):
                    token_list.append(stemmer.stem(t.group(0)))
                ranking_query(token_list, index, mapping)
                end = time.time()

                print(query, "takes: ", end - s)
                print()
