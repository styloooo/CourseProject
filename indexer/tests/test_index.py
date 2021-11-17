from django.test import TestCase
from indexer.index import ParsedDocument
from indexer.models import TermLexicon
from faker import Faker

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

class TestIndexer(TestCase):
    pass    
    # def setUp(self):
    #     self.fake = Faker()
    #     Faker.seed(0)
    #     numDocs = 5
    #     nb_sentences = 5

    #     self.docs = {}
    #     for i in range(numDocs):
    #         pageFullText = self.fake.paragraph(nb_sentences=nb_sentences)
    #         wordList = pageFullText.replace('.', '').split(' ')
    #         self.docs[self.fake.url()] = {
    #             'pageFullText': pageFullText,
    #             'wordList': wordList
    #         }

    #     self.properties = {}
    #     for key in self.docs.keys():
            

    # def testIndexerSingleDocument(self):
    #     print(self.docs)