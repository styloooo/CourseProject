from indexer.models import Document, DocumentLexicon, TermLexicon
from indexer.utils import is_alpha, is_stopword, stem 

class ParsedDocument:
    def __process_word_list(self, word_list: list[str]) -> list[str]:
        # processing wordFreqMap and wordList separately would require iterating twice
        # so let's do it in the same loop
        termFrequencyMap = {}
        wordList = []
        for word in word_list:
            word = word.lower()
            if is_alpha(word) and not is_stopword(word):
                stemmedWord = stem(word)
                if stemmedWord not in termFrequencyMap.keys():
                    termFrequencyMap[stemmedWord] = 1
                    wordList.append(stemmedWord)
                else:
                    termFrequencyMap[stemmedWord] += 1
        
        return wordList, termFrequencyMap
    
    def get_unique_terms(self):
        return self.termFrequencyMap.keys()

    def __init__(self, word_list: list[str]):
        self.wordList, self.termFrequencyMap = self.__process_word_list(word_list)

def cleanup_indexed_document(indexParams: dict) -> None:
    '''
    Deletes DocumentLexicon entries and adjusts TermLexicon frequencies for an existing Document before it is reindexed.

    indexParams: a map containing parameters for indexing
        parsedDocument:  ParsedDocument object containing stemmed word frequencies
        documentContext: Document object initialized with page URL
        docCreated:      boolean value indicating whether document was created in index
        pageURL:         String corresponding to indexed document's URL
        pageFullText:    String of document's full text
    '''
    doc = indexParams['documentContext']

    oldDocTerms = DocumentLexicon.objects.filter(context=doc)
    # Substract doc-term frequencies from corresponding TermLexicon entry
    for oldDocTerm in oldDocTerms:
        termLexiconTerm = oldDocTerm.term
        termLexiconTerm.frequency -= oldDocTerm.frequency
        termLexiconTerm.save()
        oldDocTerm.delete()


def index_document(indexParams: dict) -> None:
    '''
    Indexes a document that has not previously been indexed.

    indexParams: a map containing parameters for indexing
        parsedDocument:  ParsedDocument object containing stemmed word frequencies
        documentContext: Document object initialized with page URL
        docCreated:      boolean value indicating whether document was created in index
        pageURL:         String corresponding to indexed document's URL
        pageFullText:    String of document's full text
    '''
    doc = indexParams['documentContext']
    pDoc = indexParams['parsedDocument']

    # Needs tests
    for docTerm, parsedFrequency in pDoc.termFrequencyMap.items():
        try:
            termLexiconTerm = TermLexicon.objects.get(term=docTerm)  # need to give an initial freq - get_or_create won't work so long as freq is non-nullable
            termLexiconTerm.frequency += parsedFrequency
            termLexiconTerm.save()
        except TermLexicon.DoesNotExist:
            termLexiconTerm = TermLexicon.objects.create(term=docTerm, frequency=parsedFrequency)

        try:
            docLexiconTerm = DocumentLexicon.objects.get(context=doc, term=termLexiconTerm)
            raise RuntimeError("Found a duplicate term {termID} in DocumentLexicon that shouldn't be there".format(termID=docLexiconTerm.id))
        except DocumentLexicon.DoesNotExist:
            docLexiconTerm = DocumentLexicon.objects.create(context=doc, term=termLexiconTerm, frequency=parsedFrequency)


def index(word_list: list[str], page_title: str, page_url: str, page_full_text: str) -> None:
    pDoc = ParsedDocument(word_list)
    doc, created = Document.objects.get_or_create(url=page_url)

    # Is it OK to update these regardless of update/create?
    doc.title = page_title
    doc.text = page_full_text
    doc.save()

    indexParams = {
        'parsedDocument': pDoc,
        'documentContext': doc,
        'docCreated': created,  # may remove
        'pageTitle': page_title,  # may remove
        'pageURL': page_url,  # may remove
        'pageFullText': page_full_text  # may remove
    }

    if not created:
        cleanup_indexed_document(indexParams)

    index_document(indexParams)
        


# Indexing:
# Expect a list of words for a document from scraper with page URL + original page full text 
# After separating a document into atomic units and grouping...
# 0. Do nothing if document is already present in the index (URL) / Replace contents
# 1. Create corresponding document entry
# 2. Iterate over a doc's terms
# 3. Perform any stemming/stopword elimination
# 4. Check the TermLexicon for term's existence
# 5a. If term hasn't been added, created an entry and set its frequency to the document frequency 
# 5b. If a term has been previously added, add its document frequency to its overall frequency
# 5c. If document is being updated, subtract each term's existing doc frequency from corresponding overall doc frequency, update doc-term freq, add updated doc-term frequency to overall
