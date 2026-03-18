import os
import requests
import re
from collections import defaultdict
from random import randrange


class MarkovText(object):

    def __init__(self, corpus, pre_cleaned=False, include_repeats=True, separate_punct=False):
        # Clean the corpus data given if needed
        if pre_cleaned:
            self.corpus = corpus
        else:
            self.corpus = self.clean_data(corpus)

        # Get the term dictionary that we will use for generation
        self.term_dict = self.get_term_dict(include_repeats, separate_punct)

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

    def get_term_dict(self, include_repeats=True, separate_punt=False, debug=True):
        # We will use a defaultdict so that every key
        # will be initialized to an empty list. Then we
        # can just append to a given key's list without
        # creating that key first
        term_dict = defaultdict(list)

        # If we want to treat punctuation as separate tokens as well, they
        # need to be separated from the words. Going through in linear time
        # by character is the fastest approach for this I have tried.
        if separate_punt:
            print('Separating punctuation...')

            # Get the corpus in lowercase
            text = self.corpus.lower()

            # Characters that we accumulate between punctuation and spaces
            buffer = ''

            # The words (tokens) that we are separating
            words = []

            # Info for printing a progress bar since this could take a while
            num_chars = len(text)
            char_count = 0

            # Accumulate characters until we either hit a space or punctuation
            for char in text:
                # If it is a letter or number, add it to the buffer
                if char.isalnum():
                    buffer += char

                # If it is a space, add what we have accumulated to the word list
                elif char == ' ' and buffer != '':
                    words.append(buffer)
                    buffer = ''

                # If it is punctuation, add it to the word list
                # adding any accumulated letters first
                elif not char.isalnum() and char != ' ':
                    if buffer != '':
                        words.append(buffer)
                        buffer = ''

                    words.append(char)

                # Print a progress bar
                char_count += 1
                print(f'{100*char_count//num_chars}% checking char {char_count} of {num_chars}', end='\r')

            print('Done.')

        # If we don't mind having words with punctuation together as a token,
        # we can just split at the spaces
        else:
            words = self.corpus.lower().split(' ')


        # Now we can check every word and add the following word
        # to the dictionary depending on the repeats setting
        print('Building dictionary...')
        for i in range(len(words) - 1):
            if include_repeats or not words[i+1] in term_dict[words[i]]:
                term_dict[words[i]].append(words[i+1])

            # Print a progress bar
            print(f'Working on word {i} of {len(words)}', end='\r')

        print('Done.')

        # Return the completed dictionary
        return term_dict 


    def generate(self, seed_term=None, term_count=15):
        # Get the start term from all the words
        if seed_term is None:
            words = list(self.term_dict.keys())
            seed_term = words[randrange(len(words))]

        if not seed_term in self.term_dict.keys():
            raise ValueError('Invalid seed term. Must be a word from the corpus.')

        # Base case, if no words should be added, return an empty string
        if term_count == 0:
            return '' 

        # Get the selection of possible next words
        next_words = self.term_dict[seed_term] 

        # Pick one randomly
        next_word = next_words[randrange(len(next_words))]

        # Recursively generate more words and return them concatenated together
        return next_word + ' ' + self.generate(next_word, term_count-1)


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
    gen = MarkovText(quotes_raw, separate_punct=False)
    print(gen.generate())
