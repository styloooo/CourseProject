from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

def stem(word: str) -> str:
    stemmer = PorterStemmer()
    return stemmer.stem(word)

def is_stopword(word: str) -> bool:
    return word in stopwords.words('english')

def is_alpha(word: str) -> bool:
    return word.isalpha()

# Stem words.words() and check against it for verification?