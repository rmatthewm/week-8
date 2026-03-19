import os
import requests
import re
from collections import defaultdict
from random import randrange

class TokenWindow:
    """ A wrapper for a list that provides queue-like behavior specific to the
    sliding window used to build our MarkovText dictionary.
    """

    def __init__(self, size=1, values=None):
        # The size needs to be at least 1
        if size < 1:
            raise ValueError('Window size must be at least 1.')

        # The size of the window
        self.__size = size

        # This is the list we will use internally to store the tokens 
        self.__list = []

        # If there are initial values, add them, assuming they fit in the
        # window
        if values is not None:
            if len(values) > size:
                raise ValueError('Initial window values cannot be larger than the window size.')

            self.__list += values


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


    def get_tuple(self):
        """ Return the inner list as a tuple to use for hashing in a dictionary

        Returns:
            tuple: the current state of the sliding window of tokens 
        """
        return tuple(self.__list)

    def __getitem__(self, key):
        """ Overload the [] operators so we can access the tokens 
        in the window

        Args:
            key (int): the key for the index of the token to return 

        Returns:
            str: the token at index key 
        """
        return self.__list[key]

    def __str__(self):
        """ Overload the to string method so that we can print the window for debugging 

        Returns:
            str: the string representation of the inner list 
        """
        return str(self.__list)

    def __list__(self):
        return self.__list


class MarkovText(object):

    def __init__(self, corpus, k=1, pre_cleaned=False, include_repeats=True, separate_punct=False):
        # Clean the corpus data given if needed
        if pre_cleaned:
            self.corpus = corpus
        else:
            self.corpus = self.clean_data(corpus)

        # The window size for creating the dictionary
        self.k = k

        # Get the term dictionary that we will use for generation
        self.term_dict = self.get_term_dict(include_repeats=include_repeats, separate_punct=separate_punct)


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


    def get_term_dict(self, include_repeats=True, separate_punct=False, debug=True):
        # We will use a defaultdict so that every key
        # will be initialized to an empty list. Then we
        # can just append to a given key's list without
        # creating that key first
        term_dict = defaultdict(list)

        # If we want the punctuation to be treated as separate tokens, then 
        # separate the punctuation 
        if separate_punct:

            # Get the corpus in lower case
            text = self.corpus.lower()

            # Tokenize the corpus including separating punctuation
            words = self.separate_punctuation(text)
            
        # If we don't mind having words with punctuation together as a token,
        # we can just split at the spaces
        else:
            words = self.corpus.lower().split(' ')

        # Now we can check every window and add the following word
        # to the dictionary depending on the repeats setting.
        # Regardless of size, the last element in the window is element i.
        print('Building dictionary...')
        for i in range(len(words) - 1):
            # Get the sliding window
            if i - self.k + 1 < 0:
                window = tuple(words[:i+1])

            else:
                window = tuple(words[i-self.k+1:i+1])

            # Add the word that comes after this window, observing repeat setting
            if include_repeats or not words[i+1] in term_dict[window]:
                term_dict[window].append(words[i+1])

            # Print a progress bar
            print(f'Working on word {i} of {len(words)}', end='\r')

        print('\nDone.')

        # Return the completed dictionary
        return term_dict 


    def generate_list(self, seed_window, term_count):
        # Base case, if no words should be added, return an empty string
        if term_count == 0:
            return list(seed_window) 

        # Get the selection of possible next tokens 
        next_tokens = self.term_dict[seed_window.get_tuple()] 

        # Get the first element in the seed window as the current element in the list 
        current_token = seed_window[0]

        # Pick a token randomly and add it to the seed window 
        seed_window.add_next(next_tokens[randrange(len(next_tokens))])

        # Recursively generate more words and return as a list
        return [current_token] + self.generate_list(seed_window, term_count-1)

    def generate(self, seed_terms=None, term_count=15):
        # Get the starting window values from all the words
        # if none is given
        if seed_terms is None:
            words = list(self.term_dict.keys())
            seed_terms = words[randrange(len(words))]

        if not seed_terms in self.term_dict.keys():
            raise ValueError('Invalid seed term. Must be a word from the corpus.')

        # Create a window object using the seed terms
        seed_window = TokenWindow(self.k, seed_terms)

        # Recursively generate a list of words
        word_list = self.generate_list(seed_window, term_count)

        # Join them into a string
        return ' '.join(word_list)


# Testing
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

    # Generate the text
    gen = MarkovText(quotes_raw, k=2, separate_punct=True)
    print(gen.generate())
