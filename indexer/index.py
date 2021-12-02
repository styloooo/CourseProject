"""This module handles indexing documents"""

from indexer.models import Document, DocumentLexicon, TermLexicon
from indexer.utils import is_alpha, is_stopword, stem

class ParsedDocument:
    """
    This class normalizes a set of input words and sums their frequencies
    """
    def __process_word_list(self, word_list: list[str]) -> list[str]:
        # processing wordFreqMap and wordList separately would require iterating twice
        # so let's do it in the same loop
        term_frequency_map = {}
        processed_word_list = []
        for word in word_list:
            word = word.lower()
            if is_alpha(word) and not is_stopword(word):
                stemmed_word = stem(word)
                if stemmed_word not in term_frequency_map.keys():
                    term_frequency_map[stemmed_word] = 1
                    processed_word_list.append(stemmed_word)
                else:
                    term_frequency_map[stemmed_word] += 1

        return processed_word_list, term_frequency_map

    def get_unique_terms(self):
        """Returns a set of unique terms parsed by the instance"""
        return self.term_frequency_map.keys()

    def __init__(self, input_words: list[str]):
        self.words, self.term_frequency_map = self.__process_word_list(input_words)

def cleanup_indexed_document(index_params: dict) -> None:
    '''
    Deletes DocumentLexicon entries and adjusts TermLexicon frequencies for an existing Document
    before it is reindexed.

    indexParams: a map containing parameters for indexing
        parsedDocument:  ParsedDocument object containing stemmed word frequencies
        documentContext: Document object initialized with page URL
        docCreated:      boolean value indicating whether document was created in index
        pageURL:         String corresponding to indexed document's URL
        pageFullText:    String of document's full text
    '''
    doc = index_params['documentContext']

    old_doc_terms = DocumentLexicon.objects.filter(context=doc)
    # Substract doc-term frequencies from corresponding TermLexicon entry
    for old_doc_term in old_doc_terms:
        term_lexicon_term = old_doc_term.term
        term_lexicon_term.frequency -= old_doc_term.frequency
        term_lexicon_term.save()
        old_doc_term.delete()


def index_document(index_params: dict) -> None:
    '''
    Indexes a document that has not previously been indexed.

    indexParams: a map containing parameters for indexing
        parsedDocument:  ParsedDocument object containing stemmed word frequencies
        documentContext: Document object initialized with page URL
        docCreated:      boolean value indicating whether document was created in index
        pageURL:         String corresponding to indexed document's URL
        pageFullText:    String of document's full text
    '''
    doc = index_params['documentContext']
    p_doc = index_params['parsedDocument']

    # Needs tests
    for doc_term, parsed_frequency in p_doc.term_frequency_map.items():
        try:
            term_lexicon_term = TermLexicon.objects.get(term=doc_term)
            term_lexicon_term.frequency += parsed_frequency
            term_lexicon_term.save()
        except TermLexicon.DoesNotExist:
            term_lexicon_term = TermLexicon.objects.create(
                term=doc_term, frequency=parsed_frequency)

        try:
            doc_lexicon_term = DocumentLexicon.objects.get(
                context=doc, term=term_lexicon_term)
            raise RuntimeError(
                f"""
                Found a duplicate term {doc_lexicon_term.id}
                in DocumentLexicon that shouldn't be there
                """)
        except DocumentLexicon.DoesNotExist:
            doc_lexicon_term = DocumentLexicon.objects.create(
                context=doc, term=term_lexicon_term, frequency=parsed_frequency)


def index(word_list: list[str], page_title: str, page_url: str, page_full_text: str) -> None:
    """
    Wrapper function for indexing a document

    word_list:      a list containing words to be indexed
    page_title:     title of the page/document to be indexed
    page_url:       URL of the page/document to be indexed
    page_full_text: full text of page/document to be indexed
    """
    p_doc = ParsedDocument(word_list)
    doc, created = Document.objects.get_or_create(url=page_url)

    # Is it OK to update these regardless of update/create?
    doc.title = page_title
    doc.text = page_full_text
    doc.save()

    index_params = {
        'parsedDocument': p_doc,
        'documentContext': doc,
        'docCreated': created,  # may remove
        'pageTitle': page_title,  # may remove
        'pageURL': page_url,  # may remove
        'pageFullText': page_full_text  # may remove
    }

    if not created:
        cleanup_indexed_document(index_params)

    index_document(index_params)



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
# 5c. If document is being updated, subtract each term's existing doc frequency from corresponding
# overall doc frequency, update doc-term freq, add updated doc-term frequency to overall
