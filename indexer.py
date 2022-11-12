import os
import re
import json
from bs4 import BeautifulSoup
from json import JSONDecodeError
from nltk.stem.snowball import SnowballStemmer
from collections import defaultdict, namedtuple


class Indexer:
    def __init__(self, file_dir, index_path):
        self.stemmer = SnowballStemmer("english")
        self.pattern = re.compile(r"[a-zA-Z0-9]+")  # used to find tokens
        self.token_dict = {}
        self.file_dir = file_dir  # data source dir
        self.index_path = index_path
        if not os.path.exists(index_path):
            os.mkdir(index_path)


    def stemming(self, word):
        return self.stemmer.stem(word)


    def merge(self):
        with os.scandir(self.index_path) as it:
            pass


    def get_report(self):
        with open("report.txt", 'w') as f:
            d = set()
            size = 0
            with os.scandir(self.index_path) as it:
                for file in it:
                    size += os.path.getsize(file)
                    with open(file, 'r') as fi:
                        d.update(set(json.load(fi)))
            
            print(f"Unique words: {len(d)}", file=f)
            print(f"Total size: {size/1000} kb", file=f)
        

    
    def parse(self, content):
        '''Yield each token and relative position from the content'''
        position = 0
        soup = BeautifulSoup(content, 'lxml')

        for string in soup.stripped_strings:
            for token in self.pattern.finditer(string):
                yield self.stemming(token.group()), position
                position += 1
    

    def add_posting(self, doc_id, token, position):
        if token in self.token_dict:
            if doc_id in self.token_dict[token]:
                self.token_dict[token][doc_id]["location"].append(position)
                self.token_dict[token][doc_id]["freq"] += 1
            else:
                posting = {"location": [position], "freq": 1}
                self.token_dict[token][doc_id] = posting
            return

        posting = {"location": [position], "freq": 1}
        self.token_dict[token] = {doc_id: posting}
    

    def write(self, dir, file_name):
        with open(os.path.join(dir, file_name), 'w') as f:
            json.dump(dict(sorted(self.token_dict.items())), f)
        self.token_dict.clear()


    def build(self):
        '''Build inverted index to the specified path'''
        doc_id = 0

        for root, _, pages in os.walk(self.file_dir):  # iterate through all the pages in the file directory
            for page in pages:
                with open(os.path.join(root, page), 'rb') as f:
                    data = json.load(f)
                    for token, position in self.parse(data['content']):
                        self.add_posting(str(doc_id), token, position)

                doc_id += 1
                if doc_id % 20000 == 0:
                    self.write(self.index_path, 'index' + str(doc_id // 20000) + '.json')

        self.write(self.index_path, 'index' + str(doc_id // 20000 + 1) + '.json')



if __name__ == '__main__':
    import warnings
    warnings.simplefilter("ignore")

    file_dir = "./DEV"  # data source directory
    index_path = "./index"
    indexer = Indexer(file_dir, index_path)
    indexer.build()
    indexer.get_report()

    print("DONE")





    # def tokens_to_dict(self, tokens, url_signature, url):
    #     Poster = namedtuple("Poster", ("url", "frequency", "location"))
    #     token_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:Poster("",0,[]))))
    #     for t_tuple in tokens:
    #         t = self.stemmer.stem(t_tuple.word)
    #         position = t_tuple.position
    #         poster_pointer = token_dict[t[0]][t][url_signature]
    #         p = Poster(url, poster_pointer.frequency+1, poster_pointer.location + [position])
    #         token_dict[t[0]][t][url_signature] = p
    #         # poster_pointer.url = url
    #         # poster_pointer.frequency += 1
    #         # poster_pointer.location.append(position)
    #     # f = open("./report.txt", "w")
    #     # json.dump(token_dict,f)
    #     # f.close()
    #     # return token_dict


    # def write_index(self, token_dictionary):
    #         for sub_folder in token_dictionary:
    #             sub_path = os.path.join(self.index_path, sub_folder)
    #             if not os.path.exists(sub_path):
    #                 os.mkdir(sub_path)
    #             sub_file = os.path.join(sub_path, "token_dict.txt")
    #             try:
    #                 saved_dict = json.loads(sub_file)
    #             except JSONDecodeError as j:
    #                 saved_dict = {}
    #             # for t, Poster_dict in saved_dict.items():
    #             #     for url_signature, poster in token_dictionary[sub_path][t].items():
    #             #         saved_dict[t][url_signature] = poster
    #             #         json.dumps()
    #             for token, poster_dict in token_dictionary[sub_folder].items():
    #                 if token in saved_dict:
    #                     saved_dict[token].update(poster_dict)
    #                 else:
    #                     saved_dict[token] = poster_dict
    #                 sub = open(sub_file, "w")
    #                 json.dump(saved_dict, sub)
    #                 sub.close()


