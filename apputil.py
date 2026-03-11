import os
import requests
import re
from collections import defaultdict


class MarkovText(object):

    def __init__(self, corpus, pre_cleaned=False):
        # Clean the corpus data given if needed
        if pre_cleaned:
            self.corpus = corpus
        else:
            self.corpus = self.clean_data(corpus)

        print(self.corpus[:2000])

        self.term_dict = None  # you'll need to build this

    def clean_data(self, corpus):
        # Replace the new lines with spaces
        quotes = quotes_raw.replace('\n', ' ')

        # Split the quotes within quotes from the rest of the text
        quotes = re.split("[“”]", quotes)

        # Get every other line
        quotes = quotes[1::2]

        # Create one long corpus of text
        corpus = ' '.join(quotes)

        # Remove long whitespaces
        corpus = re.sub(r"\s+", " ", corpus)

        # Remove leading/trailing whitespaces
        corpus = corpus.strip()

        # Return the cleaned data
        return corpus

    def get_term_dict(self):

        # your code here ...

        self.term_dict = {}

        return None


    def generate(self, seed_term=None, term_count=15):

        # your code here ...

        return None

if __name__ == '__main__':
    # Get the corpus
    # We can cache it to make testing easier
    if os.path.isfile('data.txt'):
        file = open('data.txt', 'r')
        quotes_raw = file.read()
        file.close()

    else:
        # Get the data from the given url
        url = 'https://raw.githubusercontent.com/leontoddjohnson/datasets/main/text/inspiration_quotes.txt'
        content = requests.get(url)
        quotes_raw = content.text

        # Save the data to a text file
        file = open('data.txt', 'w')
        file.write(quotes_raw)
        file.close()

    # Testing
    gen = MarkovText(quotes_raw)
