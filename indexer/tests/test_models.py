from django.test import TestCase
from indexer.models import TermLexicon

# Create your tests here.
class ModelsTestCase(TestCase):
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