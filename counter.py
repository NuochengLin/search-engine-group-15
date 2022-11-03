from os import getcwd
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer


# The counter for calculating the report statistics
class Counter():
    def __init__(self):
        self.unique_page = 0         # number of unique pages
        self.longest_page = ["", 0]  # index 0: url, index 1: the number of words
        self.fdist = FreqDist()      # key: word, value: number of occurrence
        self.subdomain = FreqDist()  # key: subdomain str, value: number of unique pages

        # some helpers
        self.tokenizer = RegexpTokenizer(r"[\w'.-]+")
        self.stopwords = set(stopwords.words('english'))

    def process_soup(self, soup, url):
        text = soup.get_text("|", strip=True)
        tokens = self.tokenizer.tokenize(text)

        if len(tokens) < 245:  # check for low information pages
            return True

        # update unique page
        self.unique_page += 1

        # update word frequency dict
        word_count = 0
        for word in tokens:
            word = word.strip('.').lower()
            if word not in self.stopwords and len(word) > 1:
                self.fdist[word] += 1
                word_count += 1

        # update longest page
        if word_count > self.longest_page[1]:
            self.longest_page[0] = url.geturl()
            self.longest_page[1] = word_count

        # update subdomain
        if url.hostname and ".ics.uci.edu" in url.hostname and url.hostname != "www.ics.uci.edu":
            self.subdomain[url.hostname] += 1

        return False

    def get_report(self):
        '''Get report.txt to the current directory'''
        with open(getcwd() + '/report.txt', 'w+') as f:
            print(f'# 1. Unique pages: {self.unique_page}\n', file=f)
            print(f'# 2. The longest page:\n'
                  f'url:{self.longest_page[0]}\n'
                  f'words count: {self.longest_page[1]}\n', file=f)

            print(f'# 3. Top 50 most common words:\n'
                  f'{"word" : <20}| frequency', file=f)
            for word, freq in self.fdist.most_common(50):
                print(f'{word : <20}| {freq}', file=f)
            print(file=f)

            print(f'# 4. Subdomains:', file=f)
            for subdomain in sorted(self.subdomain.keys()):
                print(f'{subdomain}, {self.subdomain[subdomain]}', file=f)
