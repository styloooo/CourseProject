from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.porter import PorterStemmer

def stem(word):
    """Stems a word based on NLTK's PorterStemmer
    args:
        word: String of word to be stemmed

    returns:
        str: String of stemmed word
    """
    stemmer = SnowballStemmer('english')
    # stemmer = PorterStemmer()
    return stemmer.stem(word)

def is_stopword(word):
    """
    Determines whether a word is a stopword based on NLTK's stopword corpus
    args:
        word: String of word to check whether it is a stopword

    returns:
        bool: True if word is stopword
    """
    return word in stopwords.words('english')

def is_alpha(word):
    """
    Determines whether a word contains non-alphabetic characters
    args:
        word: String of word to check for non-alphabetic characters

    returns:
        bool: True if word only consists of alphabetic characters
    """
    # return word.isalpha()
    allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-'"))
    validation = set((word))
    return validation.issubset(allowed_chars)

# Stem words.words() and check against it for verification?
