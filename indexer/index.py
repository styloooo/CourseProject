class ParsedDocument:
    def __init__(self, word_list, page_url, page_full_text):
        self.word_list = word_list
        self.page_url = page_url
        self.page_full_text = page_full_text

def index(word_list, page_url, page_full_text):
    raise NotImplementedError