from django.db import models

class Document(models.Model):
    '''additional info on a document we don't want to keep in the docLexicon table'''
    title = models.CharField(max_length=255)  # taken from <title> tag on page
    url = models.URLField()
    text = models.TextField()  # raw page text for displaying some portion on retrieval (maybe 500-1000 words stored at most)

class TermLexicon(models.Model):
    term = models.CharField(max_length=500, unique=True)
    frequency = models.IntegerField()  # overall frequency in the corpus

    def __str__(self):
        return "{term} ({frequency})".format(term=self.term, frequency=self.frequency)

class DocumentLexicon(models.Model):
    context = models.ForeignKey(Document, on_delete=models.PROTECT)  # prevent deletion of FK'd rows
    term = models.ForeignKey(TermLexicon, on_delete=models.PROTECT)  # prevent deletion of FK'd rows
    frequency = models.IntegerField()  # term frequency in doc

# Retrieval:
# 0. Perform stopword elimination and stemming on query
# 1. Query each term from TermLexicon
# 2. Query each term's set of documents from DocumentLexicon
# 3. Initialize score accumulators and score each document

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