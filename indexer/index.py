from indexer.models import TermLexicon
from indexer.utils import stem, is_stopword, is_alpha

class ParsedDocument:
    def __process_word_list(self, word_list: list) -> list:
        # processing wordFreqMap and wordList separately would require iterating twice
        # so let's do it in the same loop
        wordFrequencyMap = {}
        wordList = []
        for word in word_list:
            word = word.lower()
            if is_alpha(word) and not is_stopword(word):
                stemmedWord = stem(word)
                if stemmedWord not in wordFrequencyMap.keys():
                    wordFrequencyMap[stemmedWord] = 1
                    wordList.append(stemmedWord)
                else:
                    wordFrequencyMap[stemmedWord] += 1
        
        return wordList, wordFrequencyMap
            

    def __init__(self, word_list: list):
        self.wordList, self.wordFrequencyMap = self.__process_word_list(word_list)

def is_doc_indexed(url):
    pass

def index(word_list, page_url, page_full_text):
    # pDoc = ParsedDocument(word_list)
    raise NotImplementedError

# Indexing:
# Expect a list of words for a document from scraper with page URL + original page full text 
# After separating a document into atomic units and grouping...
# 0. Do nothing if document is already present in the index (URL)
# 1. Iterate over a doc's terms
# 2. Perform any stemming/stopword elimination
# 3. Check the TermLexicon for term's existence
# 4. If term hasn't been added, created an entry and set its frequency to the document frequency 
# 5. If a term has been previously added, add its document frequency to its overall frequency
# 6. Create corresponding document entry