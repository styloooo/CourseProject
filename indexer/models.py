"""This module serves as model definitions for the indexer app"""
from django.db import models

class Document(models.Model):
    '''additional info on a document we don't want to keep in the docLexicon table'''
    title = models.CharField(max_length=255)  # taken from <title> tag on page
    url = models.URLField(unique=True)
    # raw page text for displaying some portion on retrieval
    # (maybe 500-1000 words stored at most)
    text = models.TextField()

    def __str__(self):
        return f"{self.title}: {self.url}"

class TermLexicon(models.Model):
    """overall representation of a term across all documents"""
    term = models.CharField(max_length=500, unique=True)
    frequency = models.IntegerField()  # overall frequency in the corpus

    def __str__(self):
        return f"{self.term} ({self.frequency})"

class DocumentLexicon(models.Model):
    """representation of a term within each document"""
    context = models.ForeignKey(Document, on_delete=models.PROTECT)  # prevent deletion of FK'd rows
    term = models.ForeignKey(TermLexicon, on_delete=models.PROTECT)  # prevent deletion of FK'd rows
    frequency = models.IntegerField()  # term frequency in doc

# Retrieval:
# 0. Perform stopword elimination and stemming on query
# 1. Query each term from TermLexicon
# 2. Query each term's set of documents from DocumentLexicon
# 3. Initialize score accumulators and score each document

# In Document , each document we index receives one row - this is the central
# index table for documents.
# DocumentLexicon is the model that links terms from the TermLexicon to the Document
# they were indexed from.
# TermLexicon is our model representation of the terms we index - from this model you can follow the
# Foreign Keys back to the DocumentLexicon to drill down on a term by document or follow another
# Foreign Key back to its Document representation.
