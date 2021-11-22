from django.test import TestCase
from indexer.models import TermLexicon, DocumentLexicon, Document
from faker import Faker
from indexer.utils import is_stopword, stem

from indexer.index import (
    cleanup_indexed_document,
    index_document,
    index,
    ParsedDocument,
    )

# Create your tests here.
class ParsedDocumentTestCase(TestCase):
    def setUp(self):
        self.faker = Faker()
        Faker.seed(0)

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

    def testUniqueTermKeyGetter(self):
        numWords = 10
        wordList = [
            self.faker.word() for i in range(numWords)
        ]
        parsedDoc = ParsedDocument(wordList)
        uniqueTerms = []
        for word in wordList:
            if not is_stopword(word) and word not in uniqueTerms:
                uniqueTerms.append(stem(word))
        uniqueTerms.sort()
        pDocUniqueTerms = sorted(list(parsedDoc.get_unique_terms()))
        self.assertTrue(len(uniqueTerms) == len(pDocUniqueTerms))
        self.assertTrue(uniqueTerms == pDocUniqueTerms)
        for uTerm, pTerm in zip(uniqueTerms, pDocUniqueTerms):
            self.assertTrue(uTerm == pTerm)

# class TestIndexerUpdate(TestCase):
#     def setUp(self):
#         overallFreq = 20
#         docFreq = 10
#         term = "Foo"
#         contextObj = Document.objects.create(title="Test Doc", url="http://testdoc.com/", text="f")
#         termObj = TermLexicon.objects.create(term=term, frequency=overallFreq)
#         docLexiconObj = DocumentLexicon.objects.create(context=contextObj, term=termObj, frequency=docFreq)
#         self.params = {
#             'contextObj': contextObj,
#             'termObj': termObj,
#             'docLexiconObj': docLexiconObj,
#             'term': term
#         }

#     # def testDocumentLexiconUpdate(self):
#     #     newFreq = 5
#     #     update_documentLexicon_term_frequency(self.params['docLexiconObj'], newFreq)
#     #     self.assertTrue(self.params['docLexiconObj'].frequency == newFreq)

#     # def testTermLexiconUpdate(self):
#     #     newFreq = 7
#     #     termObj = self.params['termObj']
#     #     oldOverallFreq = termObj.frequency
#     #     oldDocFreq = self.params['docLexiconObj'].frequency
#     #     update_termLexicon_term_frequency(termObj, self.params['docLexiconObj'], newFreq)
#     #     self.assertTrue(termObj.frequency == oldOverallFreq - oldDocFreq + newFreq)

#     def testIndexedDocumentCleanup(self):
#         pass

class IndexerHelpersTestCase(TestCase):
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
        
        duplicateTermKey = list(pDoc.get_unique_terms())[0]
        duplicateTermFreq = pDoc.termFrequencyMap[duplicateTermKey]
        term = TermLexicon.objects.create(term=duplicateTermKey, frequency=duplicateTermFreq)
        DocumentLexicon.objects.create(term=term, context=docContext, frequency=duplicateTermFreq)

        with self.assertRaises(RuntimeError):
            index_document({
                'documentContext': docContext,
                'parsedDocument': pDoc
            })

    def testIndexedDocumentCleanup(self):
        pDoc = self.params['pDocs'][0]
        docContext = self.params['contextObjs'][0]

        funcParams = {
            'documentContext': docContext,
            'parsedDocument': pDoc
        }

        index_document(funcParams)
        docLexiconTerms = DocumentLexicon.objects.filter(context=docContext).all()
        self.assertTrue(docLexiconTerms.count() == len(pDoc.get_unique_terms()))

        docTerms = []
        for dTerm in docLexiconTerms:
            docTerms.append(dTerm.term.term)

        cleanup_indexed_document(funcParams)
        docLexiconTerms = DocumentLexicon.objects.filter(context=docContext).all()
        self.assertTrue(docLexiconTerms.count() == 0)

        for term in docTerms:
            self.assertTrue(TermLexicon.objects.get(term=term).frequency == 0)

class IndexerWrapperTestCase(TestCase):
    def setUp(self):
        # @TODO: fix this
        self.faker = Faker()
        Faker.seed(0)
        numDocs = 5

        pDocs = []
        corpusTermFrequencies = {}
        docPartsList = []

        for num in range(numDocs):
            text = self.faker.paragraph(nb_sentences=25)
            title = self.faker.text(max_nb_chars=50).title()
            url = self.faker.url()
            wordList = text.replace('.', '').split(' ')
            pDoc = ParsedDocument(wordList)
            pDocs.append(pDoc)
            docPartsList.append(
                {
                    'url': url,
                    'text': text,
                    'title': title,
                    'wordList': wordList
                }
            )
            for term in pDoc.get_unique_terms():
                if term not in corpusTermFrequencies.keys():
                    corpusTermFrequencies[term] = pDoc.termFrequencyMap[term]
                else:
                    corpusTermFrequencies[term] += pDoc.termFrequencyMap[term]

        self.params = {
            'pDocs': pDocs,
            'corpusTermFrequencies': corpusTermFrequencies,
            'docPartsList': docPartsList,
        }

    def testOverwriteDocument(self):
        # @TODO: review this
        pDocOrig = self.params['pDocs'][0]
        pDocUpdate = self.params['pDocs'][1]

        docPartsOrig = self.params['docPartsList'][0]
        docPartsUpdate = self.params['docPartsList'][1]

        origWordList = docPartsOrig['wordList']
        origPageTitle = docPartsOrig['title']
        origText = docPartsOrig['text']
        origURL = docPartsOrig['url']
        origWordList = docPartsOrig['wordList']

        updatedWordList = docPartsUpdate['wordList']
        updatedText = docPartsUpdate['text']

        index(origWordList, origPageTitle, origURL, origText)
        index(updatedWordList, origPageTitle, origURL, updatedText)

        docContext = Document.objects.get(url=origURL)

        for term in pDocOrig.get_unique_terms():
            termLexiconTerm = TermLexicon.objects.get(term=term)
            if term not in pDocUpdate.get_unique_terms():
                self.assertTrue(termLexiconTerm.frequency == 0)
            else:
                self.assertTrue(termLexiconTerm.frequency == pDocUpdate.termFrequencyMap[termLexiconTerm.term])

        for term in pDocUpdate.get_unique_terms():
            docLexiconTerm = DocumentLexicon.objects.get(
                context=docContext,
                term=TermLexicon.objects.get(term=term)
            )
            self.assertTrue(docLexiconTerm.frequency == pDocUpdate.termFrequencyMap[docLexiconTerm.term.term])

    def testIndexWrapperSingleDocument(self):
        pDoc = self.params['pDocs'][0]

        docParts = self.params['docPartsList'][0]        
        pageTitle = docParts['title']
        text = docParts['text']
        url = docParts['url']
        wordList = docParts['wordList']

        index(wordList, pageTitle, url, text)

        termLexiconTerms = TermLexicon.objects.all()
        docContext = Document.objects.get(url=url)
        docLexiconTerms = DocumentLexicon.objects.filter(context=docContext).all()

        self.assertTrue(len(pDoc.get_unique_terms()) == termLexiconTerms.count() == docLexiconTerms.count())

        for term in termLexiconTerms:
            self.assertTrue(term.frequency == pDoc.termFrequencyMap[term.term])

        for term in docLexiconTerms:
            self.assertTrue(term.frequency == pDoc.termFrequencyMap[term.term.term])

    def testIndexWrapperMultipleDocuments(self):
        corpusTermFrequencies = self.params['corpusTermFrequencies']

        for docParts in self.params['docPartsList']:
            docURL = docParts['url']
            docText = docParts['text']
            docTitle = docParts['title']
            docWordList = docParts['wordList']

            index(docWordList, docTitle, docURL, docText)

        termLexiconTerms = TermLexicon.objects.all()
        self.assertTrue(len(corpusTermFrequencies.keys()) == termLexiconTerms.count())

        for termObj in termLexiconTerms:
            termStr = termObj.term
            testTermFreq = corpusTermFrequencies[termStr]
            self.assertTrue(termObj.frequency == testTermFreq)

        for idx, docParts in enumerate(self.params['docPartsList']):
            url = docParts['url']
            pDoc = self.params['pDocs'][idx]
            doc = Document.objects.get(url=url)
            docTerms = DocumentLexicon.objects.filter(context=doc).all()

            self.assertTrue(len(pDoc.get_unique_terms()) == docTerms.count())

            for docTerm in docTerms:
                termStr = docTerm.term.term
                pDocTermFreq = pDoc.termFrequencyMap[termStr]
                self.assertTrue(docTerm.frequency == pDocTermFreq)
