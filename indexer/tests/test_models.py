from django.test import TestCase
from indexer.models import TermLexicon, Document

# Create your tests here.
class TermLexiconTestCase(TestCase):
    def setUp(self):
        TermLexicon.objects.create(term="foo", frequency=5)
        TermLexicon.objects.create(term="bar", frequency=1)
        TermLexicon.objects.create(term="baz", frequency=123456)

    def test_termLexicon_str_function(self):
        foo = TermLexicon.objects.get(term="foo")
        bar = TermLexicon.objects.get(term="bar")
        baz = TermLexicon.objects.get(term="baz")

        self.assertEqual(str(foo), "foo (5)")
        self.assertEqual(str(bar), "bar (1)")
        self.assertEqual(str(baz), "baz (123456)")

class DocumentTestCase(TestCase):
    def setUp(self):
        self.foo = {
            'url': "http://foo.com/",
            'title': 'All The Foos',
        }
        self.bar = {
            'url': "http://bar.org/",
            'title': 'The Bar Org',
        }
        Document.objects.create(url=self.foo['url'], title=self.foo['title'], text="f")
        Document.objects.create(url=self.bar['url'], title=self.bar['title'], text="b")

    def test_document_str_function(self):
        foo = Document.objects.get(url=self.foo['url'])
        bar = Document.objects.get(url=self.bar['url'])

        self.assertTrue(str(foo) == "{title}: {url}".format(title=self.foo['title'], url=self.foo['url']))
        self.assertTrue(str(bar) == "{title}: {url}".format(title=self.bar['title'], url=self.bar['url']))
