# Authored by Kee Dong (yuqingd2)

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

from indexer.retrieve import (
    parse_query,
    get_total_documents,
    get_total_related_documents,
    compute_idf_corpus,
    compute_tf_idf_query,
    compute_tf_idf_document,
    cosine_similarity_query_document,
    retrieve
    )

# Create your tests here.
class ParsedQueryTestCase(TestCase):
    def setUp(self):
        self.faker = Faker()
        Faker.seed(0)

    def testEmptyInput(self):
        parsedQuery = parse_query("")
        self.assertTrue(len(parsedQuery) == 0)

    def testSimpleStemmedInputWithStopWords(self):
        query = "I want to eat an apple"
 
        baselineFreqMap = {
            'appl': 1,
            'want': 1, 
            'eat': 1
        }

        parsedQuery = parse_query(query)
        self.assertTrue(len(parsedQuery) == 3)

        for parsedWord in parsedQuery.keys():
            self.assertTrue(parsedQuery[parsedWord] == baselineFreqMap[parsedWord])


class RetrieverHelpersTestCase(TestCase):
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
            for term, frequency in pDoc.term_frequency_map.items():
                if term not in corpusTermFrequencies.keys():
                    corpusTermFrequencies[term] = pDoc.term_frequency_map[term]
                else:
                    corpusTermFrequencies[term] += pDoc.term_frequency_map[term]

        self.params = {
            'contextObjs': contextObjs,
            'pDocs': pDocs,
            'corpusTermFrequencies': corpusTermFrequencies,
        }


    def testTotalDocCount(self):
        total_documents = get_total_documents()
        self.assertTrue(total_documents == 5)

    def testTotalRelatedDocuments(self):
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

        relatedDocCount = []
        for pDoc, docContext in zip(pDocs, contextObjs):
            for term, docTermFrequency in pDoc.term_frequency_map.items():
                termObj = TermLexicon.objects.get(term=term)
                relatedDocCount.append(get_total_related_documents(termObj))
                  # check that per-doc term freqs were set properly
        #print(relatedDocCount)
        # self.assertTrue(len(relatedDocCount) == len(pDocs))
      
    def testComputeIdfCorpus(self):
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
        idf_corpus = compute_idf_corpus()
        self.assertTrue(len(idf_corpus) == TermLexicon.objects.all().count())


    def testComputeTfIdfQuery(self):
        pDocs = self.params['pDocs']
        contextObjs = self.params['contextObjs']

        for pDoc, docContext in zip(pDocs, contextObjs):
            index_document({
                'documentContext': docContext,
                'parsedDocument': pDoc
            })

        query = "american food"
        idf_corpus = compute_idf_corpus()
        tf_idf_query = compute_tf_idf_query(query, idf_corpus)
        # print (tf_idf_query)
        self.assertTrue(len(tf_idf_query) == 2)

    def testComputeTfIdfDocument(self):
        pDocs = self.params['pDocs']
        contextObjs = self.params['contextObjs']

        for pDoc, docContext in zip(pDocs, contextObjs):
            index_document({
                'documentContext': docContext,
                'parsedDocument': pDoc
            })

        idf_corpus = compute_idf_corpus()
        tf_idf_doc = compute_tf_idf_document(contextObjs[1], idf_corpus)
        # print (tf_idf_doc)


    def testSimilartityScore(self):
        pDocs = self.params['pDocs']
        contextObjs = self.params['contextObjs']

        for pDoc, docContext in zip(pDocs, contextObjs):
            index_document({
                'documentContext': docContext,
                'parsedDocument': pDoc
            })


        query = "better american food"
        idf_corpus = compute_idf_corpus()
        tf_idf_doc = compute_tf_idf_document(contextObjs[1], idf_corpus)
        tf_idf_query = compute_tf_idf_query(query, idf_corpus)
        cossim = cosine_similarity_query_document(tf_idf_query, tf_idf_doc)
        # print (cossim)


    def testRetrieveMain(self):
        pDocs = self.params['pDocs']
        contextObjs = self.params['contextObjs']

        for pDoc, docContext in zip(pDocs, contextObjs):
            index_document({
                'documentContext': docContext,
                'parsedDocument': pDoc
            })

        query = "better american food"
        ranked_list = retrieve(query)
        # print (ranked_list)
        self.assertTrue(len(ranked_list) == 5)

