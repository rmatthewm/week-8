import os
import requests
import re
from collections import defaultdict
from random import randrange


class MarkovText(object):

    def __init__(self, corpus, pre_cleaned=False, include_repeats=True):
        # Clean the corpus data given if needed
        if pre_cleaned:
            self.corpus = corpus
        else:
            self.corpus = self.clean_data(corpus)

        # Get the term dictionary that we will use for generation
        self.term_dict = self.get_term_dict(include_repeats)

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

    def get_term_dict(self, include_repeats=True):
        # We will use a defaultdict so that every key
        # will be initialized to an empty list. Then we
        # can just append to a given key's list without
        # creating that key first
        term_dict = defaultdict(list)

        # Split the corpus into words
        words = self.corpus.split(' ')

        # Now we can check every word and add the following word
        # to the dictionary depending on the repeats setting
        for i in range(len(words) - 1):
            # We will make everything lowercase first before checking or adding
            if include_repeats or not words[i+1].lower() in term_dict[words[i].lower()]:
                term_dict[words[i].lower()].append(words[i+1].lower())

        return term_dict 


    def generate(self, seed_term=None, term_count=15):
        # Get the start term from all the words
        if seed_term is None:
            words = list(self.term_dict.keys())
            seed_term = words[randrange(len(words))]

        # Now run generate some number of times
        gen_list = [seed_term]
        for i in range(1, randrange(5, 20)):
            # Get the selection of possible next words
            next_words = self.term_dict[gen_list[i-1]] 

            # Pick one randomly and add it
            gen_list.append(next_words[randrange(len(next_words))])

        # Join the words together as a string and return it
        return ' '.join(gen_list)

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
    print(gen.generate())
