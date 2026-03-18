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

        # Split the corpus into words
        words = self.corpus.lower().split(' ')

        # Currently, a single word could contain multiple tokens if we want
        # to separate punctuation, so we need to check if there is punctuation
        # before or after to remove.
        percent_complete = 0
        if separate_punt:
            print('Separating punctuation tokens.')
            # We cannot use a for loop because we are potentially lengthening the list
            i = 0
            while i < len(words) - 1:
                # For each word, we can separate it into all its tokens then 
                # insert it into the list again.
                word_tokens = [] 
                trailing_tokens = []
                word = words[i]

                # Add any leading punctuation as separate tokens
                while len(word) > 1 and not word[0].isalnum():
                    word_tokens.append(word[0])
                    word = word[1:]

                # Add any trailing punctuation as separate tokens 
                while len(word) > 1 and not word[-1].isalnum():
                    trailing_tokens.append(word[-1])
                    word = word[:-1]
                
                # Reverse the trailing_tokens because we added them moving backwards
                # and add it to the word tokens along with the word itself
                trailing_tokens.reverse()
                word_tokens.append(word)
                word_tokens += trailing_tokens

                # We need to splice the newly separated tokens back into the original list
                if i == 0:
                    words = word_tokens + words[1:]

                elif i == len(words) - 1:
                    words = words[:i] + word_tokens

                else:
                    words = words[:i] + word_tokens + words[i+1:]
                
                # Update i to be the next word after the splice
                i = i + len(word_tokens)

                print(f'Working on word {i} of {len(words)}', end='\r')
                # if i // len(words) > percent_complete:
                #     percent_complete = i // len(words)
                #     print(f'{percent_complete} complete.')

            print()
 

        # Now we can check every word and add the following word
        # to the dictionary depending on the repeats setting
        print('Building dictionary')
        percent_complete = 0
        for i in range(len(words) - 1):
            if include_repeats or not words[i+1] in term_dict[words[i]]:
                term_dict[words[i]].append(words[i+1])

            print(f'Working on word {i} of {len(words)}', end='\r')
            # if i // len(words) > percent_complete:
            #     percent_complete = i // len(words)
            #     print(f'{percent_complete} complete.')
        print()

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
    gen = MarkovText(quotes_raw, separate_punct=True)
    print(gen.generate())
