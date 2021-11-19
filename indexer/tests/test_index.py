from django.test import TestCase
from indexer.models import TermLexicon, DocumentLexicon, Document
from faker import Faker

from indexer.index import (
    ParsedDocument,
    index_document,
    update_documentLexicon_term_frequency,
    update_termLexicon_term_frequency,
    )

# Create your tests here.
class ParsedDocumentTestCase(TestCase):

    def testEmptyInput(self):
        parsedDoc = ParsedDocument([])
        self.assertTrue(len(parsedDoc.wordList) == 0)
        self.assertTrue(len(parsedDoc.termFrequencyMap) == 0)

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
        parsedMap = parsedDoc.termFrequencyMap
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
        self.assertTrue(len(parsedDoc.termFrequencyMap) == 0)

class TestIndexerUpdate(TestCase):
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

    def testMultipleDocUpdate(self):
        pass

class TestIndexerInsert(TestCase):
    def setUp(self):
        self.faker = Faker()
        Faker.seed(0)
        numDocs = 5

        contextObjs = []
        pDocs = []
        corpusTermFrequencies = {}

        for num in range(numDocs):
            text = self.faker.paragraph(nb_sentences=25)
            title = self.faker.text(max_nb_chars=50).title()
            url = self.faker.url()
            contextObj = Document.objects.create(title=title, url=url, text=text)
            contextObjs.append(contextObj)
            wordList = text.replace('.', '').split(' ')
            pDoc = ParsedDocument(wordList)
            pDocs.append(pDoc)
            for term, frequency in pDoc.termFrequencyMap.items():
                if term not in corpusTermFrequencies.keys():
                    corpusTermFrequencies[term] = pDoc.termFrequencyMap[term]
                else:
                    corpusTermFrequencies[term] += pDoc.termFrequencyMap[term]

        self.params = {
            'contextObjs': contextObjs,
            'pDocs': pDocs,
            'corpusTermFrequencies': corpusTermFrequencies,
        }

    def testSingleDocIndex(self):
        pDoc = self.params['pDocs'][0]
        docContext = self.params['contextObjs'][0]
        
        index_document({
            'documentContext': docContext,
            'parsedDocument': pDoc
        })

        for term, frequency in pDoc.termFrequencyMap.items():
            overallTerm = TermLexicon.objects.get(term=term)
            docTerm = DocumentLexicon.objects.get(term=overallTerm, context=docContext)
            self.assertTrue(frequency == overallTerm.frequency)
            self.assertTrue(frequency == docTerm.frequency)

    def testMultipleDocIndex(self):
        pDocs = self.params['pDocs']
        contextObjs = self.params['contextObjs']
        corpusTermFrequencies = self.params['corpusTermFrequencies']

        for pDoc, docContext in zip(pDocs, contextObjs):
            index_document({
                'documentContext': docContext,
                'parsedDocument': pDoc
            })
        
        for term, frequency in corpusTermFrequencies.items():
            overallTerm = TermLexicon.objects.get(term=term)
            self.assertTrue(frequency == overallTerm.frequency)  # check that overall term freqs were set properly

        for pDoc, docContext in zip(pDocs, contextObjs):
            for term, docTermFrequency in pDoc.termFrequencyMap.items():
                termObj = TermLexicon.objects.get(term=term)
                docTerm = DocumentLexicon.objects.get(context=docContext, term=termObj)
                self.assertTrue(docTermFrequency == docTerm.frequency)  # check that per-doc term freqs were set properly

    def testDuplicateDocumentTermInsertion(self):
        pDoc = self.params['pDocs'][0]
        docContext = self.params['contextObjs'][0]
        
        duplicateTermKey = list(pDoc.termFrequencyMap.keys())[0]
        duplicateTermFreq = pDoc.termFrequencyMap[duplicateTermKey]
        term = TermLexicon.objects.create(term=duplicateTermKey, frequency=duplicateTermFreq)
        DocumentLexicon.objects.create(term=term, context=docContext, frequency=duplicateTermFreq)

        with self.assertRaises(RuntimeError):
            index_document({
                'documentContext': docContext,
                'parsedDocument': pDoc
            })
