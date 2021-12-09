# Authored by Kee Dong (yuqingd2)

from indexer.models import Document, DocumentLexicon, TermLexicon
from indexer.utils import is_alpha, is_stopword, stem 
import math

def parse_query(query):
    word_list = query.split()
    query_term_frequency_map = {}
    for word in word_list:
        word = word.lower()
        if is_alpha(word) and not is_stopword(word):
            stemmed_word = stem(word)
            if stemmed_word not in query_term_frequency_map.keys():
                query_term_frequency_map[stemmed_word] = 1
            else:
                query_term_frequency_map[stemmed_word] += 1
        
    return query_term_frequency_map

def get_total_documents():
    #query index table to get total number of documents
    return Document.objects.all().count()

def get_total_related_documents(term):
    #takes term object as input
    #query index table on number of documents who has the input term
    return DocumentLexicon.objects.filter(term=term).count()
    
def inverse_document_frequency(term):
    #takes term object as input
    N = get_total_documents()
    N_t = get_total_related_documents(term)
    
    if N_t > 0:
        return 1.0 + math.log(N / N_t)
    else:
        return 1.0
    
def compute_idf_corpus():
    idf_corpus = {}
    term_set = TermLexicon.objects.all()
    for t in term_set.iterator():
        idf_corpus[t.term] = inverse_document_frequency(t)

    return idf_corpus
        
def compute_tf_idf_query(query, idf_corpus):
    tf_idf_query = {}
    query_term_frequency_map = parse_query(query)
    for word in query_term_frequency_map.keys():
        tf = query_term_frequency_map[word]
        # smoothed_tf = math.log(1+tf)
        smoothed_tf = math.log(1.2+tf)
        if word in idf_corpus.keys():
            tf_idf_query[word] = smoothed_tf * idf_corpus[word]
        else:
            tf_idf_query[word] = smoothed_tf

    return tf_idf_query

def compute_tf_idf_document(document, idf_corpus):
    tf_idf_document = {}
    lex_objs = DocumentLexicon.objects.filter(context=document)
    for t in lex_objs.iterator():
        termobj = t.term
        word = termobj.term
        smoothed_tf = math.log(1.2+t.frequency)
        tf_idf_document[word] = smoothed_tf * idf_corpus[word]

    return tf_idf_document

    
def cosine_similarity_query_document(tf_idf_query, tf_idf_document):
    dot_product = 0
    qry_mod = 0
    doc_mod = 0
   
    for word in tf_idf_query.keys():
        if word not in tf_idf_document.keys():
            tf_idf_document_term = math.log(1.2)
        else:
            tf_idf_document_term = tf_idf_document[word]
        
        dot_product += tf_idf_query[word] * tf_idf_document_term
        #||Query||
        qry_mod += tf_idf_query[word] * tf_idf_query[word]
        #||Document||
        doc_mod += tf_idf_document_term * tf_idf_document_term
    qry_mod = math.sqrt(qry_mod)
    doc_mod = math.sqrt(doc_mod)
    #implement formula
    denominator = qry_mod * doc_mod
    cos_sim = dot_product/denominator
    return cos_sim


def retrieve(query):
    idf_corpus = compute_idf_corpus()
    tf_idf_query = compute_tf_idf_query(query, idf_corpus)
    
    similarity = {}
    all_docs = Document.objects.all()
    
    for doc in all_docs.iterator():
        tf_idf_document = compute_tf_idf_document(doc, idf_corpus)
        doc_sim = cosine_similarity_query_document(tf_idf_query, tf_idf_document)
        if doc_sim <= 0.997441:  # completely non-similar documents are currently output as 1.0
            similarity[doc] = doc_sim
    print(similarity)
    
    # ranked_similarity = tuple(sorted(similarity.items(), key=lambda item: item[1], reverse=True))
    # print(similarity)
    ranked_similarity = tuple(sorted(similarity, key=similarity.get, reverse=True))

    return ranked_similarity
