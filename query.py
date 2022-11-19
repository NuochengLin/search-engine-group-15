import shelve
from nltk.stem.snowball import SnowballStemmer
import re, math
import os
import heapq

index_path = "./index"  # data source directory
file_dir = "./DEV"  # index folder
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

def ranking_query(query):
    pattern = re.compile(r"[a-zA-Z0-9]+")
    stemmer = SnowballStemmer("english")
    with shelve.open(os.path.join(index_path, 'inverted_index'), flag='c', writeback=True) as index:
        with shelve.open(os.path.join(file_dir, 'id_url'), flag='c') as mapping:
            token_list = set()
            candidate = set()
            for t in pattern.finditer(query):
                word = stemmer.stem(t.group(0))
                if word in index:
                    for d in index[word]:
                        if d != "idf":
                            candidate.add(d)
                    token_list.add(word)
            # bool_result = intersect(*sorted(token_list, key= lambda x:len(x)))
            # print(bool_result)
            print(len(candidate))
            heap = []
            for d in candidate:
                contain = 0
                score = 0
                for term in token_list:
                    contain += 1
                    score += index[term][d]["w"] * index[term]["idf"]
                if contain/len(token_list) >= 0.75:
                    heapq.heappush(heap, (-score, d))
            for score, id in heap[:10]:
                print(id, ": ", mapping[id], "with score: ",-score, end = "\n")
query = input("Please enter your query: ")
ranking_query(query)
