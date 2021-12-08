# from django.shortcuts import render
from django.views.generic import FormView, ListView
from django.urls import reverse
# from django.http import HttpResponseServerError
from indexer.forms import URLForm, QueryForm
from indexer.scraper import scrape
from indexer.retrieve import retrieve
from indexer.index import index
from indexer.models import Document

# Create your views here.
class IndexDocumentView(FormView):
    template_name = 'indexer/index_index.html'
    form_class = URLForm
    success_url = '/'


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['slug'] = 'indexer-index'
        if 'scraped_url' in self.request.session.keys():
            context['scraped_url'] = self.request.session['scraped_url']
        if 'scraped_status_code' in self.request.session.keys():
            context['scraped_status_code'] = self.request.session['scraped_status_code']
        if 'page_was_scraped' in self.request.session.keys():
            context['page_was_scraped'] = True
        else:
            context['page_was_scraped'] = False
        self.request.session.flush()
        return context

    def form_valid(self, form):
        if form.is_valid():
            # print(f"Scraping {url}...")
            url = form.cleaned_data['url']
            self.request.session['scraped_url'] = url
            scrape_results = scrape(url)
            page_is_scraped_successfully = scrape_results[0]
            page_status_code = scrape_results[1]['status_code']
            self.request.session['scraped_status_code'] = page_status_code
            self.request.session['page_was_scraped'] = True
            if page_is_scraped_successfully:
                if page_status_code == 200:
                    word_list = scrape_results[1]['word_list']
                    page_full_text = scrape_results[1]['page_full_text']
                    page_title = scrape_results[1]['page_title']
                    index(word_list, page_title, url, page_full_text)
                else:
                    print(f'error: {page_status_code}')
            else:
                print('page not found')

        return super().form_valid(form)

class QueryDocumentView(FormView):
    template_name = 'indexer/index_query.html'
    form_class = QueryForm
    # success_url = 'indexer-results'
    query = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['slug'] = 'indexer-search'
        return context

    def form_valid(self, form):
        self.query = form.cleaned_data['query']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('indexer-results', kwargs={'query': self.query})

class RetrievedDocumentView(ListView):
    model = Document
    paginate_by = 100
    template_name = 'indexer/index_query_results.html'
    query = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # self.query = self.kwargs.get('query')
        context['query'] = self.query
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        self.query = self.kwargs.get('query')
        try:
            doc_IDs = retrieve(self.query)
        except NotImplementedError:
            doc_IDs = []
            print(f'Processing query {self.query}...')
        if doc_IDs:
            qs.filter(pk__in=doc_IDs)

        return qs
