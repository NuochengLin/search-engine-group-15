import os
import re
import json
import shelve  # dict-like structure to store index
from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer



class Indexer:
    def __init__(self, file_dir, index_path):
        self.file_dir = file_dir  # data source dir
        self.index_path = index_path
        self.stemmer = SnowballStemmer("english")
        self.pattern = re.compile(r"[a-zA-Z0-9]+")  # used to split tokens

        if not os.path.exists(index_path):
            os.mkdir(index_path)


    def stemming(self, word):
        return self.stemmer.stem(word)


    def get_report(self):
        with open("report.txt", 'w') as f:
            path = os.path.join(self.index_path, 'inverted_index')

            with shelve.open(os.path.join(self.index_path, 'id_url'), flag='r') as mapping:
                print(f"Number of indexed documents: {len(mapping)}", file=f)

            with shelve.open(path, flag='r') as index_file:
                print(f"Unique words: {len(index_file)}", file=f)
                print(f"Total size: {os.path.getsize(path) / 1000} kb", file=f)


    def parse(self, content):
        '''Yield each token and relative position from the content'''
        position = 0
        soup = BeautifulSoup(content, 'lxml')

        for string in soup.stripped_strings:
            for token in self.pattern.finditer(string):
                yield self.stemming(token.group()), position
                position += 1


    def add_posting(self, doc_id, token, position, index_file):
        if token in index_file:  # append to exist entry
            if doc_id in index_file[token]:
                index_file[token][doc_id]["location"].append(position)
                index_file[token][doc_id]["freq"] += 1

            else:  # create new doc_id for token
                posting = {"location": [position], "freq": 1}
                index_file[token][doc_id] = posting

        else:  # create entry for new token
            posting = {"location": [position], "freq": 1}
            index_file[token] = {doc_id: posting}


    def build(self):
        '''Build inverted index to the specified path'''
        doc_id = 0  # doc id starts at 0

        with shelve.open(os.path.join(self.index_path, 'inverted_index'), flag='c', writeback=True) as index_file:
            with shelve.open(os.path.join(self.index_path, 'id_url'), flag='c') as mapping:  # create doc_id to url mapping file

                for root, _, pages in os.walk(self.file_dir):  # iterate through all the pages in the file directory
                    for page in pages:
                        with open(os.path.join(root, page), 'rb') as f:
                            data = json.load(f)  # parse page json to data
                            mapping[str(doc_id)] = data['url']  # mapping doc_id to url

                            for token, position in self.parse(data['content']):  # get each token from that page
                                self.add_posting(str(doc_id), token, position, index_file)  # add posting to the index file on cache

                        doc_id += 1

            index_file.sync()  # write back to file and empty the cache




if __name__ == '__main__':
    import warnings
    warnings.simplefilter("ignore")

    file_dir = "./DEV"  # data source directory
    index_path = "./index"  # index folder
    indexer = Indexer(file_dir, index_path)
    indexer.build()
    indexer.get_report()

    print("DONE")

