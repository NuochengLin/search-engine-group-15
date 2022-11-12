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
        self.file_dir = file_dir  # data source dir
        self.index_path = index_path
        if not os.path.exists(index_path):
            os.mkdir(index_path)


    def stemming(self, word):
        return self.stemmer.stem(word)


    def tokens_to_dict(self, tokens, url_signature, url):
        Poster = namedtuple("Poster", ("url", "frequency", "location"))
        token_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:Poster("",0,[]))))
        for t_tuple in tokens:
            t = self.stemmer.stem(t_tuple.word)
            position = t_tuple.position
            poster_pointer = token_dict[t[0]][t][url_signature]
            p = Poster(url, poster_pointer.frequency+1, poster_pointer.location + [position])
            token_dict[t[0]][t][url_signature] = p
            # poster_pointer.url = url
            # poster_pointer.frequency += 1
            # poster_pointer.location.append(position)
        f = open("./report.txt", "w")
        json.dump(token_dict,f)
        f.close()
        return token_dict


    def write_index(self, token_dictionary):
            for sub_folder in token_dictionary:
                sub_path = os.path.join(self.index_path, sub_folder)
                if not os.path.exists(sub_path):
                    os.mkdir(sub_path)
                sub_file = os.path.join(sub_path, "token_dict.txt")
                try:
                    saved_dict = json.loads(sub_file)
                except JSONDecodeError as j:
                    saved_dict = {}
                # for t, Poster_dict in saved_dict.items():
                #     for url_signature, poster in token_dictionary[sub_path][t].items():
                #         saved_dict[t][url_signature] = poster
                #         json.dumps()
                for token, poster_dict in token_dictionary[sub_folder].items():
                    if token in saved_dict:
                        saved_dict[token].update(poster_dict)
                    else:
                        saved_dict[token] = poster_dict
                    sub = open(sub_file, "w")
                    json.dump(saved_dict, sub)
                    sub.close()


    def index(self, tokens, url_signature, url):
        token_dict = self.tokens_to_dict(tokens, url_signature, url)
        self.write_index(token_dict)
    
    
    def parse(self, content):
        '''Yield each token and relative position from the content'''
        position = 0
        soup = BeautifulSoup(content, 'lxml')

        for string in soup.stripped_strings:
            for token in self.pattern.finditer(string):
                yield self.stemming(token.group()), position
                position += 1
    
    
    def build(self):
        '''Build inverted index to the specified path'''
        doc_id = 0

        for root, _, pages in os.walk(self.file_dir):  # iterate through all the pages in the file directory
            for page in pages:
                with open(os.path.join(root, page), 'rb') as f:
                    data = json.load(f)
                    for token, position in self.parse(data['content']):
                        print(token, position)
                        

                doc_id += 1
                        
                                


if __name__ == '__main__':
    import warnings
    warnings.simplefilter("ignore")

    file_dir = "./DEV"  # data source directory
    index_path = "./index"
    indexer = Indexer(file_dir, index_path)
    indexer.build()
    print("DONE")







# import json
#
# from nltk.stem import PorterStemmer
# import os
# from collections import defaultdict, namedtuple
# class indexer:
#     def __init__(self, index_path):
#         self.stemmer = PorterStemmer()
#         self.index_path = index_path
#         if not os.path.exists(index_path):
#             os.mkdir(index_path)
#     def stemming(self, word):
#         word = str.lower(word)
#         word = self.stemmer.stem(word)
#         return word
#     def tokens_to_dict(self, tokens, url_signature, url):
#         Poster = namedtuple("Poster", ("url", "frequency", "location"))
#         token_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:Poster("",0,[]))))
#         for t_tuple in tokens:
#             t = self.stemmer(t_tuple.word)
#             position = t_tuple.position
#             poster_pointer = token_dict[t[0]][t][url_signature]
#             poster_pointer.url = url
#             poster_pointer.frequency += 1
#             poster_pointer.location.append(position)
#         return token_dict
#     def write_index(self, token_dictionary):
#             for sub_folder in token_dictionary:
#                 sub_path = os.path.join(self.index_path, sub_folder)
#                 saved_dict = json.loads(sub_path)
#                 # for t, Poster_dict in saved_dict.items():
#                 #     for url_signature, poster in token_dictionary[sub_path][t].items():
#                 #         saved_dict[t][url_signature] = poster
#                 #         json.dumps()
#                 for token, poster_dict in token_dictionary[sub_path].items():
#                     saved_dict[token].update(poster_dict)
#                     json.dumps(saved_dict)








