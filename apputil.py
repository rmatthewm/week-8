import os
import requests
import re
from collections import defaultdict
from random import randrange

class TokenWindow:
    """ A wrapper for a list that provides queue-like behavior specific to the
    sliding window used to build our MarkovText dictionary.
    """

    def __init__(self, size=1):
        """ Constructor """
        # The size needs to be at least 1
        if size < 1:
            raise ValueError('Window size must be at least 1.')

        # The size of the window
        self.__size = size

        # This is the list we will use internally to store the tokens 
        self.__list = []


    def add_next(self, token):
        """ Add another token to the end of the window, and if the window 
        is at its max size, remove the first item, effectively "sliding"
        the window.

        Args:
            token (str): the next token to slide the window over 
        """
        self.__list.append(token)
        if len(self.__list) > self.__size:
            self.__list.pop(0) 


    def to_tuple(self):
        """ Return the inner list as a tuple to use for hashing in a dictionary

        Returns:
            tuple: the current state of the sliding window of tokens 
        """
        return tuple(self.__list)


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


    def separate_punctuation(self, text):
        """ Separates the punctuation in a text as separate tokens and returns
        the list of all tokens in order

        Going through in linear time character by character is the fastest 
        approach for this I have tried.

        Args:
            text (str): the text to be tokenized 

        Returns:
            list(str): the list of tokens 
        """

        print('Separating punctuation...')

        # Characters that we accumulate between punctuation and spaces
        buffer = ''

        # The tokens that we are separating
        tokens = []

        # Info for printing a progress bar since this could take a while
        num_chars = len(text)
        char_count = 0

        # Accumulate characters until we either hit a space or punctuation
        for char in text:
            # If it is a letter or number, add it to the buffer
            if char.isalnum():
                buffer += char

            # If it is a space, add what we have accumulated to the token list
            elif char == ' ' and buffer != '':
                tokens.append(buffer)
                buffer = ''

            # If it is punctuation, add it to the token list
            # adding any accumulated letters first
            elif not char.isalnum() and char != ' ':
                if buffer != '':
                    tokens.append(buffer)
                    buffer = ''

                tokens.append(char)

            # Print a progress bar
            char_count += 1
            print(f'{100*char_count//num_chars}% checking char {char_count} of {num_chars}', end='\r')

        print('\nDone.')

        return tokens


    def get_term_dict(self, include_repeats=True, separate_punt=False, debug=True):
        # We will use a defaultdict so that every key
        # will be initialized to an empty list. Then we
        # can just append to a given key's list without
        # creating that key first
        term_dict = defaultdict(list)

        # If we want the punctuation to be treated as separate tokens, then 
        # separate the punctuation 
        if separate_punt:

            # Get the corpus in lower case
            text = self.corpus.lower()

            # Tokenize the corpus including separating punctuation
            words = self.separate_punctuation(text)
            
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

        print('\nDone.')

        # Return the completed dictionary
        return term_dict 


    def generate(self, seed_term=None, term_count=15, k=1):
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
