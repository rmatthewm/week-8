import os
import requests
import re
import hashlib
from collections import defaultdict
from random import randrange
from token_window import TokenWindow


class MarkovText(object):

    def __init__(self, corpus, k=1, pre_cleaned=False, include_repeats=True, separate_punct=False, cached=True, verbose=False):
        # Clean the corpus data given if needed
        if pre_cleaned:
            self.corpus = corpus
        else:
            self.corpus = self.clean_data(corpus)

        # The window size for creating the dictionary
        self.k = k

        # Whether or not to cache the dictionary to avoid long processing times later on
        self.cached = cached

        # Whether or not to print progress bars and info while processing data
        self.verbose = verbose

        # Get the term dictionary that we will use for generation
        self.term_dict = self.get_term_dict(include_repeats=include_repeats, separate_punct=separate_punct)


    def clean_data(self, corpus):
        """ Clean the data as outlined in the exercise

        Args:
            corpus (str): the text to be cleaned

        Returns:
            str: the text after cleaning 
        """
        # Replace the new lines with spaces
        quotes = corpus.replace('\n', ' ')

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

        if self.verbose:
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
            if self.verbose:
                char_count += 1
                print(f'{100*char_count//num_chars}% checking char {char_count} of {num_chars}', end='\r')

        if self.verbose:
            print('\nDone.')

        return tokens


    def get_term_dict(self, include_repeats=True, separate_punct=False):
        """ Create the dictionary that will be used to generate the words

        Args:
            include_repeats (bool, optional): whether to include duplicate words to affect
            the probability of the word being chosen. Defaults to True.

            separate_punct (bool, optional): whether to treat punctuation as separate tokens. Defaults to False.

        Returns:
            dict: the dictionary of terms 
        """
        # Hash the first 200 lines of the corpus, the k value, and punctuation 
        # setting to get a unique id for this dictionary 
        id_data = self.corpus[:200] + str(self.k) + str(separate_punct)
        id_data_bytes = id_data.encode('utf-8')
        dict_hash = hashlib.sha256(id_data_bytes).hexdigest()

        # Check if there is a dictionary cached with this id
        if os.path.exists(f'MarkovCache/{dict_hash}.txt') and self.cached:

            if self.verbose:
                print('Loading data from cache...')

            
            # If there is, we will read in the term dictionary from the cache
            with open(f'MarkovCache/{dict_hash}.txt', 'r') as file:
                text = file.read().strip()

            text = text.split('\n')

            term_dict = {}

            for line in text:
                # Ignore any blank lines
                if line == '':
                    continue

                # Split the lines using our custom separator
                key, values = line.split('<||>')

                # Then split the keys and values and add them to the dictionary
                key_tuple = tuple(key.split(' ')) 
                term_dict[key_tuple] = values.split(' ')

            if self.verbose:
                print('Done.')

            # Return the loaded dictionary
            return term_dict


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

        if self.verbose:
            print('Building dictionary...')

        # Now we can check every window and add the following word
        # to the dictionary depending on the repeats setting.
        # Regardless of size, the last element in the window is element i.
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
            if self.verbose:
                print(f'Working on word {i} of {len(words)}', end='\r')

        if self.verbose:
            print('\nDone.')

        # If caching is set to be true, save the term dictionary using
        # the hash from above as the file name. 
        if self.cached:
            if self.verbose:
                print('Saving dictionary...') 

            # If the caching folder doesn't exist, create it
            if not os.path.exists('MarkovCache'):
                os.mkdir('MarkovCache')

            # Save the dictionary as our own custom format since we have 
            # various punctuation marks inside 
            with open(f'MarkovCache/{dict_hash}.txt', 'a') as file:
                for key in list(term_dict.keys()):
                    # First we will separate all values within a window by spaces
                    line = ' '.join(key)

                    # Then add a separator that is unlikely to occur in any text
                    line += '<||>'

                    # Then add the following words separated by spaces
                    line += ' '.join(term_dict[key])
                    line += '\n'

                    # Write the line
                    file.write(line)

            if self.verbose:
                print('Done.')

        # Return the completed dictionary
        return term_dict 


    def generate_list(self, seed_window, term_count):
        """ Generate a single word and add it to the list returned, recurse term_count times

        Args:
            seed_window (TokenWindow): the window of words that came before what we are going to generate
            term_count (int): the number of words to generate in total

        Returns:
            list(str): a list of generated words
        """
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

    def generate(self, seed_term=None, term_count=15):
        """ Generates a string of length term_count + 1 by adding one word at a time

        Args:
            seed_term (str, optional): a word to start with. Defaults to None.
            term_count (int, optional): the number of words/tokens to generate. Defaults to 15.

        Raises:
            ValueError: if the seed_term given is not in the dictionary

        Returns:
            str: the generated string
        """
        # Get the starting window values from all the words
        # if none is given
        if seed_term is None:
            words = list(self.term_dict.keys())
            seed_terms = words[randrange(len(words))]
        else:
            seed_terms = [seed_term] 

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
    gen = MarkovText(quotes_raw, k=1, separate_punct=True, cached=True)
    print(gen.generate())
