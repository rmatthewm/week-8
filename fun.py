# Play around with generating text based on other corpuses

import re
from apputil import MarkovText 

def main():
    # Read in the text data
    with open('KJV.txt', 'r') as file:
        text_data = file.read()

    # Clean the data
    text_data = text_data.replace('[', ' ')
    text_data = text_data.replace(']', ' ')
    text_data = text_data.strip()

    # Remove the reference numbers
    lines = text_data.split('\n')[2:]
    for i in range(len(lines)):
        line = lines[i].split('\t', 1)[1]
        lines[i] = line

    text_data = ' '.join(lines)
    text_data = re.sub(r"\s+", " ", text_data)

    # Create the generator
    gen = MarkovText(text_data, pre_cleaned=True, separate_punct=True)
    print(gen.generate())

if __name__ == '__main__':
    main()