from django.core.management.base import BaseCommand, CommandError
from indexer.index import index
from indexer.scraper import scrape

class Command(BaseCommand):
    help = 'Seeds the database with some documents'

    def handle(self, *args, **options):
        urls = (
            'https://www.nytimes.com/2021/12/07/us/politics/biden-putin-ukraine-summit.html?name=styln-russia-ukraine',
            'https://www.nytimes.com/2021/12/08/world/europe/nato-ukraine-russia-dilemma.html',
            'https://en.wikipedia.org/wiki/Ukraine',
            'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html',
            'https://books.toscrape.com/catalogue/soumission_998/index.html',
            'https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html',
            'https://www.goodreads.com/en/book/show/30118.A_Light_in_the_Attic',
            'https://www.washingtonpost.com/technology/2021/12/08/instagram-adam-mosseri-child-safety-hearing/',
            'https://www.chicagotribune.com/news/criminal-justice/ct-jussie-smollett-trial-closings-verdict-20211208-2tr4veoskrdc7iwbyobf2b33ni-story.html',
            'https://books.toscrape.com/catalogue/foolproof-preserving-a-guide-to-small-batch-jams-jellies-pickles-condiments-and-more-a-foolproof-guide-to-making-small-batch-jams-jellies-pickles-condiments-and-more_978/index.html',
            'https://stackoverflow.com/questions/10052220/advantages-to-using-urlfield-over-textfield',
            'https://stackoverflow.com/questions/26028200/why-is-django-creating-my-textfield-as-a-varchar-in-the-postgresql-database?rq=1',
        )

        num_successfully_indexed = 0
        for url in urls:
            print(f'Scraping {url}...')
            scrape_results = scrape(url)
            if scrape_results[0] and scrape_results[1]['status_code'] == 200:
                print('Page scraped successfully.')
                word_list = scrape_results[1]['word_list']
                page_title = scrape_results[1]['page_title']
                page_full_text = scrape_results[1]['page_full_text']
                print(f'Indexing...')
                index(word_list, page_title, url, page_full_text)
                print(f'Page indexed successfully.')
                num_successfully_indexed += 1
            else:
                print('Error encountered while scraping.')
        print(f'{num_successfully_indexed} documents successfully indexed.')
