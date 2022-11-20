import shelve
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
import re
import os
import time


pattern = re.compile(r"[a-zA-Z0-9]+")
stemmer = SnowballStemmer("english")


def parse_query(query):
    """Extract and return a list of terms from the query."""
    return [stemmer.stem(t) for t in pattern.findall(query)]


def rank(query, index):
    """Rank results by decreasing order of scores."""
    scores = defaultdict(int)

    for term in query:
        if term in index and index[term]["idf"] > 0.2:
            for d, posting in index[term].items():
                if d != "idf":
                    scores[d] += index[term]["idf"] * posting["w"]

    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def get_page(results, page=1, per_page=10):
    """Get a subset of the results.
    
    Keyword arguments:
    page     -> current page
    per_page -> number of items per page
    """
    end = page * per_page
    start = end - per_page

    if len(results) < end:
        return results[start:]
    else:
        return results[start:end]


def print_results(results, mapping):
    for id, score in results:
        print(f"{id}: {mapping[id]} with score: {round(score, 4)}")


def run():
    with shelve.open(os.path.join("./index", 'inverted_index'), flag='w', writeback=True) as index:
        with shelve.open(os.path.join("./index", 'id_url'), flag='w') as mapping:
            while True:
                query = input("Enter your query: ")
                if query == "quit":
                    break

                start = time.time()
                results = rank(parse_query(query), index)
                end = time.time()

                print_results(get_page(results, 1, 5), mapping)
                print(f"Total {len(results):,} results ({round(end - start, 3)} seconds)")
                print("Type quit to exit")
                print()



if __name__ == "__main__":
    with shelve.open(os.path.join("./index", 'inverted_index'), flag='w', writeback=True) as index:
        with shelve.open(os.path.join("./index", 'id_url'), flag='w') as mapping:
            query_list = ["cristina lopes", "machine learning", "ACM", "master of software engineering"]
            for query in query_list:
                print("----------------------------------")
                print("start processing query", query, ": ")

                start = time.time()
                results = rank(parse_query(query), index)
                end = time.time()

                print_results(get_page(results, 1, 5), mapping)
                print(f"Total {len(results):,} results ({round(end - start, 3)} seconds)")
                print()


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


# def ranking_query(query, index, mapping):
#     token_list = set()
#     candidate = set()
#     for word in query:
#         if word in index and index[word]["idf"] > 0.2:
#             for d in index[word]:
#                 if d != "idf":
#                     candidate.add(d)
#             token_list.add(word)
#     # bool_result = intersect(*sorted(token_list, key= lambda x:len(x)))
#     # print(bool_result)
#     heap = []
#     for d in candidate:
#         contain = 0
#         score = 0
#         for term in token_list:
#             contain += 1
#             if d in index[term]:
#                 score += index[term][d]["w"] * index[term]["idf"]
#         if contain / len(token_list) >= 0.75:
#             heapq.heappush(heap, (-score, d))
#     for score, id in heap[:5]:
#         print(id, ": ", mapping[id], "with score: ", -score, end="\n")
