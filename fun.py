# Play around with generating text based on other corpuses

import re
import os
import requests
import pandas as pd
from apputil import MarkovText 
from collections import defaultdict

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

    # I'm creating this dataframe here for now because I intend to run the below in a loop
    # with different k values
    # A data frame representing the dictionary created for a text with window size k.
    # size is the number of windows in the term_dict and the #_opt are the number of
    # windows with # options to choose from
    df_markov_windows = pd.DataFrame(columns=['text', 'k', 'size', '1_opt', '2_opt', '3_opt', '4_opt', '5+_opt'])

    # Run for several different combinations of k values and texts and record the results
    for corpus in texts: 
        for k in range(1, 6):
            print(f'Loading corpus {corpus[0]} with k={k}.')
            # Generate the generator
            gen = MarkovText(corpus[1], pre_cleaned=(corpus[0] != 'quotes'), k=k, separate_punct=True, verbose=True)

            # Print a quote for fun while we're here
            print(f'\nGenerating a quote from {corpus[0]} with k={k}: {gen.generate()}\n')

            # NOTE: I originally used pandas to process this part as well,
            # but it said it needed 26 GB of space for the dataframe and it
            # could not allocate it. So even though I've been trying to use
            # pandas more to explore using it, I would have had to modify the
            # dictionary first anyway just to be able to create a dataframe from
            # it, and at that point it's just simpler to cut out pandas all together.

            # The number of windows with i + 1 number of options.
            # When i = 4, it includes windows with 5 or more options 
            option_size_counts = [0] * 5 

            # Get the term dictionary
            term_dict = gen.term_dict

            for key in list(term_dict.keys()):
                # Increment the count for the number of options for this key
                if len(term_dict[key]) >= 5:
                    option_size_counts[4] += 1

                else:
                    option_size_counts[len(term_dict[key])-1] += 1 

            # Now we can use pandas to store the data from this run
            df_markov_windows.loc[len(df_markov_windows)] = [corpus[0], k, sum(option_size_counts), option_size_counts[0], 
                    option_size_counts[1], option_size_counts[2], option_size_counts[3], option_size_counts[4]]

    # Save the results 
    df_markov_windows.to_csv('fun_results.csv')
    print('Results saved.')


if __name__ == '__main__':
    main()
