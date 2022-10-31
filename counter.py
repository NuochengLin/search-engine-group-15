import os
from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words


# The counter for calculating the report statistics
class Counter():
    def __init__(self):
        self.unique_page = 0  # number of unique pages
        self.longest_page = ["", 0]  # index 0: url, index 1: the number of words
        self.fdist = FreqDist()  # key: word, value: number of occurrence
        self.subdomain = FreqDist()  # key: subdomain str, value: number of unique pages

        # some helpers
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.stopwords = set(get_stop_words('en'))


    def process_soup(self, soup, url):
        text = soup.get_text("|", strip=True)
        tokens = self.tokenizer.tokenize(text)

        # update unique page
        self.unique_page += 1

        # update longest page
        if len(tokens) > self.longest_page[1]:
            self.longest_page[0] = url.geturl()
            self.longest_page[1] = len(tokens)

        # update word frequency dict
        for word in tokens:
            if len(word) > 1:
                word = word.lower()
                if word not in self.stopwords:
                    self.fdist[word] += 1

        # update subdomain
        if "ics.uci.edu" in url.netloc and url.netloc != "www.ics.uci.edu":
            self.subdomain[url.netloc] += 1


    def get_report(self):
        '''Get report.txt to the current directory'''
        with open(os.getcwd() + '/report.txt', 'w+') as f:
            print(f'# 1. Unique pages: {self.unique_page}\n', file=f)
            print(f'# 2. The longest page:\n'
                  f'url:{self.longest_page[0]}\n'
                  f'words count: {self.longest_page[1]}\n', file=f)

            print(f'# 3. Top 50 most common words:\n'
                  f'{"word" : <20}| frequency', file=f)
            for word, freq in self.fdist.most_common(50):
                print(f'{word : <20}| {freq}', file=f)
            print(f'\n', file=f)

            print(f'# 4. Subdomains:', file=f)
            for subdomain in sorted(self.subdomain.keys()):
                print(f'{subdomain}, {self.subdomain[subdomain]}', file=f)

