import json
import os, re
import shelve  # dict-like structure to store index
from math import log10, sqrt
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer


class Indexer:
    def __init__(self, file_dir, index_path):
        self.file_dir = file_dir  # data source dir
        self.index_path = index_path
        self.stemmer = SnowballStemmer("english")
        self.pattern = re.compile(r"[a-zA-Z0-9]+")  # used to split terms

        if not os.path.exists(index_path):
            os.mkdir(index_path)


    def stemming(self, word):
        return self.stemmer.stem(word)


    def get_report(self):
        with open("report.txt", 'w') as f:
            path = os.path.join(self.index_path, 'inverted_index')

            with shelve.open(os.path.join(self.index_path, 'id_url'), flag='r') as mapping:
                print(f"Number of indexed documents: {len(mapping)}", file=f)

            with shelve.open(path, flag='r') as index:
                print(f"Unique words: {len(index)}", file=f)
                print(f"Total size: {os.path.getsize(path) / 1000} kb", file=f)


    def _parse(self, content):
        '''Yield each term and relative position from the content'''
        position = 0
        soup = BeautifulSoup(content, 'lxml')

        for string in soup.stripped_strings:
            for term in self.pattern.finditer(string):
                yield self.stemming(term.group()), position
                position += 1


    def _add_posting(self, doc_id, term, position, index):
        if term in index:  # append to exist entry
            if doc_id in index[term]:
                index[term][doc_id]["location"].append(position)
                index[term][doc_id]["freq"] += 1

            else:  # create new doc_id for term
                posting = {"location": [position], "freq": 1}
                index[term][doc_id] = posting

        else:  # create entry for new term
            posting = {"location": [position], "freq": 1}
            index[term] = {doc_id: posting}


    def _weight(self, N, index):
        """Calculate weights for the ranking model
        
        N   -> total number of documents
        idf -> inverse document frequency of term t
        w   -> length-normalized weight with respect to term t and document d
        """
        d = defaultdict(int)

        for _, postings in index.items():
            for doc_id, fields in postings.items():
                tf_wt = 1 + log10(fields["freq"])
                d[doc_id] += tf_wt ** 2

        for term, postings in index.items():
            for doc_id, fields in postings.items():
                tf_wt = 1 + log10(fields["freq"])
                length = sqrt(d[doc_id])
                fields["w"] = tf_wt / length
                del fields["freq"]

            index[term]["idf"] = log10(N / len(postings))  # idf of term = log(N / df)      


    def build(self):
        '''Build inverted index to the specified path'''
        doc_id = 0  # doc id starts at 0

        with shelve.open(os.path.join(self.index_path, 'inverted_index'), flag='c', writeback=True) as index:
            with shelve.open(os.path.join(self.index_path, 'id_url'), flag='c') as mapping:  # create doc_id to url mapping file

                for root, _, pages in os.walk(self.file_dir):  # iterate through all the pages in the file directory
                    for page in pages:
                        with open(os.path.join(root, page), 'rb') as f:
                            data = json.load(f)  # parse page json to data
                            mapping[str(doc_id)] = data['url']  # mapping doc_id to url

                            for term, position in self._parse(data['content']):  # get each term from that page
                                self._add_posting(str(doc_id), term, position, index)  # add posting to the index file on cache

                        doc_id += 1

            self._weight(doc_id + 1, index)  # calculate document weights
            index.sync()  # write back to file and empty the cache



if __name__ == '__main__':
    import warnings
    warnings.simplefilter("ignore")

    file_dir = "./DEV"  # data source directory
    index_path = "./index"  # index folder

    indexer = Indexer(file_dir, index_path)
    indexer.build()
    indexer.get_report()
    print("DONE")

