from requests import get, ConnectionError
from bs4 import BeautifulSoup

def get_words(full_page_text):
    return full_page_text.split(" ")

def get_full_page_text(raw_page_text):
    lines = (line.strip() for line in raw_page_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    text = text.replace('\n', ' ')
    return text

def scrape(url):
    """
    Scrapes a list of words from a given web page

    url: url of page to scrape

    Returns:
        a tuple of True and dict of word_list, page_text, and page_title when page was successfully scraped
        a tuple of False and dict of status_code when something went wrong on request
    """
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }
    try:
        request = get(url, headers=headers)
    except ConnectionError:
        return False, {'status_code': None}

    status_code = request.status_code

    if status_code != 200:
        return False, {'status_code': status_code}

    soup = BeautifulSoup(request.text, 'html.parser')

    for script in soup(['script', 'style']):
        script.decompose()

    page_title = soup.title.text.strip()
    page_raw_text = soup.get_text()
    page_full_text = get_full_page_text(page_raw_text)
    word_list = get_words(page_full_text)
    return True, {
        'status_code': status_code,
        'word_list': word_list,
        'page_full_text': page_full_text,
        'page_title': page_title
    }
