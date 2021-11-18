from django.test import TestCase
from indexer.models import TermLexicon, DocumentLexicon, Document
from faker import Faker

from indexer.index import (
    ParsedDocument,
    update_documentLexicon_term_frequency,
    update_termLexicon_term_frequency,
    )

# Create your tests here.
class ParsedDocumentTestCase(TestCase):

    def testEmptyInput(self):
        parsedDoc = ParsedDocument([])
        self.assertTrue(len(parsedDoc.wordList) == 0)
        self.assertTrue(len(parsedDoc.wordFrequencyMap) == 0)

    def testSimpleStemmedInputWithStopWords(self):
        wordList = [
            'a',  # stopword
            'an', # stopword
            'apples',
            'apples',
            'apples',
            'banana',
            'bananas',
            'mango',
            'oranges',
            'pear',
            'persimmon',
            'the', # stopword
            "is", # stopword
            "should've", # stopword,
            "wasn't" # stopword
        ] 

        baselineFreqMap = {
            'appl': 3,
            'banana': 2, 
            'mango': 1,
            'orang': 1,
            'pear': 1,
            'persimmon': 1,
        }

        parsedDoc = ParsedDocument(wordList)
        self.assertTrue(len(parsedDoc.wordList) == 6)
        parsedMap = parsedDoc.wordFrequencyMap
        for parsedWord in parsedMap.keys():
            self.assertTrue(parsedMap[parsedWord] == baselineFreqMap[parsedWord])

    def testInputOnlyStopWords(self):
        wordList = [
            'a',
            'an',
            'is',
            'the',
            'to',
            'was',
            "should've",
            "wasn't"
        ] 

        parsedDoc = ParsedDocument(wordList)
        self.assertTrue(len(parsedDoc.wordList) == 0)
        self.assertTrue(len(parsedDoc.wordFrequencyMap) == 0)

class TestIndexerUpdateFunctions(TestCase):
    def setUp(self):
        overallFreq = 20
        docFreq = 10
        term = "Foo"
        contextObj = Document.objects.create(title="Test Doc", url="http://testdoc.com/", text="f")
        termObj = TermLexicon.objects.create(term=term, frequency=overallFreq)
        docLexiconObj = DocumentLexicon.objects.create(context=contextObj, term=termObj, frequency=docFreq)
        self.params = {
            'contextObj': contextObj,
            'termObj': termObj,
            'docLexiconObj': docLexiconObj,
            'term': term
        }

    def testDocumentLexiconUpdate(self):
        newFreq = 5
        update_documentLexicon_term_frequency(self.params['docLexiconObj'], newFreq)
        self.assertTrue(self.params['docLexiconObj'].frequency == newFreq)

    def testTermLexiconUpdate(self):
        newFreq = 7
        termObj = self.params['termObj']
        oldOverallFreq = termObj.frequency
        oldDocFreq = self.params['docLexiconObj'].frequency
        update_termLexicon_term_frequency(termObj, self.params['docLexiconObj'], newFreq)
        self.assertTrue(termObj.frequency == oldOverallFreq - oldDocFreq + newFreq)
