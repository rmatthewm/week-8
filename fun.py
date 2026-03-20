# Play around with generating text based on other corpuses

import re
import os
import requests
from apputil import MarkovText 

def get_quotes():
    """ Get the corpus of quotes

    Returns:
        str: the text of the quotes
    """
    # We can cache it to make testing easier
    if os.path.isfile('data.txt'):
        file = open('data.txt', 'r')
        quotes_text = file.read()
        file.close()

    else:
        # Get the data from the given url
        url = 'https://raw.githubusercontent.com/leontoddjohnson/datasets/main/text/inspiration_quotes.txt'
        content = requests.get(url)
        quotes_text = content.text

        # Save the data to a text file
        file = open('data.txt', 'w')
        file.write(quotes_text)
        file.close()

    return quotes_text

def get_kjv():
    """ Load the cleaned KJV corpus

    Returns:
        str: the text of the KJV with verse numbers removed 
    """

    # Read in the text data
    with open('KJV.txt', 'r') as file:
        text_data = file.read()

    # Clean the data from the KJV text 
    text_data = text_data.replace('[', ' ')
    text_data = text_data.replace(']', ' ')
    text_data = text_data.strip()

    # Remove the reference numbers
    lines = text_data.split('\n')[2:]
    for i in range(len(lines)):
        line = lines[i].split('\t', 1)[1]
        lines[i] = line

    text_data = ' '.join(lines)
    return re.sub(r"\s+", " ", text_data)


def main():
    # Get the texts
    quotes_corpus = get_quotes()
    kjv_corpus = get_kjv()

    # Create the generators
    quotes_gen = MarkovText(quotes_corpus, k=1, separate_punct=True)
    kjv_gen = MarkovText(kjv_corpus, pre_cleaned=True, k=1, separate_punct=True)

    print(quotes_gen.generate())
    print(kjv_gen.generate())

if __name__ == '__main__':
    main()
