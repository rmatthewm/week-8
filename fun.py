# Play around with generating text based on other corpuses

import re
import os
import requests
import pandas as pd
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

    # Remove extra spaces
    return re.sub(r"\s+", " ", text_data)

def get_rv():
    with open('RV1909.txt', 'r') as file:
        text_data = file.read().lower()

    # Split the text into lines
    text_lines = text_data.split('\n') 

    # Remove the intro and end notes
    text_lines = text_lines[146:4195]

    # Put it back together and clean the data
    text_data = ' '.join(text_lines)
    text_data.replace('\n', ' ')
    text_data.replace('\t', ' ')
    text_data = text_data.replace('[', ' ')
    text_data = text_data.replace(']', ' ')

    # Remove the references
    text_data.replace('capítulo', '')
    for i in range(10):
        # I think we can just remove all of the numbers, because any
        # numbers in the text will be spelled out 
        text_data.replace(f'{i}', '')
    
    # Remove extra spaces
    return re.sub(r"\s+", " ", text_data)


def main():
    # Get the texts
    quotes_corpus = get_quotes()
    kjv_corpus = get_kjv()
    rv_corpus = get_rv()

    # Organize the texts with their names so that we can loop through them
    texts = [('quotes', quotes_corpus), ('kjv', kjv_corpus), ('rv', rv_corpus)]

    # Create the generators
    quotes_gen = MarkovText(quotes_corpus, k=1, separate_punct=True)
    #kjv_gen = MarkovText(kjv_corpus, pre_cleaned=True, k=1, separate_punct=True)
    #rv_gen = MarkovText(rv_corpus, pre_cleaned=True, k=1, separate_punct=True)

    print(quotes_gen.generate())
    #print(kjv_gen.generate())total_windows
    #print(rv_gen.generate())

    # I'm creating this dataframe here for now because I intend to run the below in a loop
    # with different k values
    # A data frame representing the dictionary created for a text with window size k.
    # size is the number of windows in the term_dict and the #_opt are the number of
    # windows with # options to choose from
    df_markov_windows = pd.DataFrame(columns=['text', 'k', 'size', '1_opt', '2_opt', '3_opt', '4_opt', '5+_opt'])

    # Use pandas to find the number of options after each window
    # The first problem we have is that all the arrays are different lengths,
    # so we will have to treat them as rows instead of columns 
    df_raw = pd.DataFrame.from_dict(quotes_gen.term_dict, orient='index')

    # Now we can transpose the dataframe since pandas has filled in the empty values
    df_raw = df_raw.T

    # Now we can get the count of the options for each window
    option_counts = df_raw.agg('count')

    # And get the number of windows with with each count
    option_size_counts = option_counts.value_counts()

    # Find the total number of windows in the dictionary
    total_windows = option_size_counts.sum()

    # Add the info to the markov windows dataframe
    df_markov_windows.loc[len(df_markov_windows)] = ['quotes', 1, total_windows, option_size_counts[1], 
            option_size_counts[2], option_size_counts[3], option_size_counts[4], option_size_counts.iloc[4:].sum()]

    print(df_markov_windows.head())


if __name__ == '__main__':
    main()
