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

