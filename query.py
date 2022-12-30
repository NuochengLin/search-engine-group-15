import shelve
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import re
import os
import time


pattern = re.compile(r"[a-zA-Z0-9]+")
stemmer = SnowballStemmer("english")
stopwords = {stemmer.stem(t) for t in stopwords.words('english')}


def parse_query(query):
    """Extract and return a list of terms from the query."""
    return {stemmer.stem(t) for t in pattern.findall(query)}


def rank(query, index):
    """Rank results by decreasing order of scores."""
    scores = defaultdict(int)

    for term in query:
        if term not in stopwords and term in index:
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
        with shelve.open(os.path.join("./index", 'id_url'), flag='r') as mapping:
            while True:
                query = input("Enter your query: ")
                if query == "quit" or not query:
                    break

                start = time.time()
                results = rank(parse_query(query), index)
                end = time.time()

                print_results(get_page(results, 1, 5), mapping)
                print(f"Total {len(results):,} results ({round(end - start, 3)} seconds)")
                print("Type quit or hit enter to exit")
                print()


def process_results(results, mapping):
    """Process results for web api."""
    items = []

    for i, r in enumerate(results):
        item = {"rank": i + 1, "url": mapping[r[0]]}
        items.append(item)
    
    return items


def search(terms):
    with shelve.open(os.path.join("./index", 'inverted_index'), flag='w', writeback=True) as index:
        with shelve.open(os.path.join("./index", 'id_url'), flag='r') as mapping:
            start = time.time()
            results = rank(terms, index)
            end = time.time()

            return process_results(results, mapping), f'({round(end - start, 3)} seconds)'


if __name__ == "__main__":
    run()

