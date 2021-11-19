from indexer.models import Document, DocumentLexicon, TermLexicon
from indexer.utils import is_alpha, is_stopword, stem 

class ParsedDocument:
    def __process_word_list(self, word_list: list) -> list:
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
            

    def __init__(self, word_list: list):
        self.wordList, self.termFrequencyMap = self.__process_word_list(word_list)

def update_documentLexicon_term_frequency(existingDocTerm: DocumentLexicon, newFrequency: int) -> None:
    '''
    Adjusts document-term frequencies when updating a document that has been previously indexed.
    Determines whether newFrequency == existingDocTerm.frequency before updating anything.

    existingDocTerm: DocumentLexicon object corresponding to updated docTerm
    newFrequency: Frequency to which DocumentLexicon term frequency should be set
    '''
    if existingDocTerm.frequency != newFrequency:
        existingDocTerm.frequency = newFrequency
        existingDocTerm.save()

def __update_termLexicon_term_frequency(term: TermLexicon, existingDocTerm: DocumentLexicon, oldFrequency: int) -> None:
    '''
    Adjusts overall term frequencies in TermLexicon when updating documents that have previously been indexed.
    Determines whether oldFrequency == existingDocTerm.frequency before updating anything.
    This function *only* updates the TermLexicon - DocumentLexicon object must be updated before calling.

    term: TermLexicon object corresponding to entry that needs to be updated
    existingDocTerm: DocumentLexicon object corresponding to existing document term frequency (before update)
    oldFrequency: frequency of a term before DocumentLexicon object was updated
    '''
    if existingDocTerm.frequency != oldFrequency:
        term.frequency -= oldFrequency
        term.frequency += existingDocTerm.frequency
        term.save()

def update_termLexicon_term_frequency(term: TermLexicon, existingDocTerm: DocumentLexicon, newFrequency: int) -> None:
    oldFrequency = existingDocTerm.frequency
    update_documentLexicon_term_frequency(existingDocTerm, newFrequency)
    __update_termLexicon_term_frequency(term, existingDocTerm, oldFrequency)

def update_indexed_document(indexParams: dict) -> None:
    '''
    Updates a document that has previously been indexed.

    indexParams: a map containing parameters for indexing
        parsedDocument:  ParsedDocument object containing stemmed word frequencies
        documentContext: Document object initialized with page URL
        docExists:       boolean value indicating whether document already existed in index
        pageURL:         String corresponding to indexed document's URL
        pageFullText:    String of document's full text
    '''
    pass

def index_document(indexParams: dict) -> None:
    '''
    Indexes a document that has not previously been indexed.

    indexParams: a map containing parameters for indexing
        parsedDocument:  ParsedDocument object containing stemmed word frequencies
        documentContext: Document object initialized with page URL
        docExists:       boolean value indicating whether document already existed in index
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


def index(word_list: list, page_title: str, page_url: str, page_full_text: str) -> None:
    pDoc = ParsedDocument(word_list)
    doc, exists = Document.objects.get_or_create(url=page_url)

    # Is it OK to update these regardless of update/create?
    doc.title = page_title
    doc.text = page_full_text
    doc.save()

    indexParams = {
        'parsedDocument': pDoc,
        'documentContext': doc,
        'docExists': exists,  # may remove
        'pageTitle': page_title,  # may remove
        'pageURL': page_url,  # may remove
        'pageFullText': page_full_text  # may remove
    }

    if exists:
        update_indexed_document(indexParams)
    else:
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
