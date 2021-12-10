# CourseProject

Please fork this repository and paste the github link of your fork on Microsoft CMT. Detailed instructions are on Coursera under Week 1: Course Project Overview/Week 9 Activities.

# Requirements
Project built using Python 3.9.2
Django 3.2.9

# Presentation Slides
Please note that a PowerPoint version of our slides are available to be downloaded [here](https://uofi.box.com/s/1bwnz9fz1rvgbaohxhniwct7cl146dq7). Additionally, a PDF version of our slides is available in this repository.

# Video
Our video can be downloaded [here](https://uofi.box.com/s/b01tt5j9vawb63pn6hqdhm45x08p1fd4).

# (1) Overview of the Project
SaveIt is a web application that enables a user to index a web page by entering a URL for later full-text search retrieval. This web application could serve as a foundational platform on which extensions for page indexing and retrieval could later be built. 
Indexing pages for full text retrieval has utility in research and hobby applications in enabling a user to save a useful page without needing to document exactly what is on that page.

# (2) Implementation Details
SaveIt is implemented in Python 3 using the Django web server framework. It is primarily composed of three modules and a models file that defines our database structure:

## <a name="models">indexer.models</a>
### File name: `indexer/models.py`

The data are split across three models:

### Document
`Document` represents the document that is being indexed. It contains basic attributes such as document `title` and `url` and it is also where a page's `full_text` is saved for display purposes on retrieval. Additionally, terms that appear within a document are linked to the `Document` model via a foreign key in the `DocumentLexicon` model. `url` has a `unique=True` constraint, thus serving as a secondary Primary Key on this table ensuring that one URL can only be indexed once and must be updated thereafter.

### TermLexicon
`TermLexicon` represents all terms that have been indexed by the system thus far. It has two attributes: `term` and `frequency`.

`term` is the string-based representation of a term that has been indexed. This is the baseline representation of a term in the system. The corresponding `term` attribute in `DocumentLexicon` is foreign keyed to the `TermLexicon`.`term` to ensure normalization across the data. This flexibility enables us to query all documents in which a queried `term` appears by following foreign keys to the `DocumentLexicon` and `Document` models. 

`frequency` defines the frequency with which a specific term appears in the collection.

### DocumentLexicon
`DocumentLexicon` represents terms on a per-document basis. It is nearly identical to `TermLexicon`; however, it does not contain a string-based representation of each indexed term. Its `term` attribute is a foreign key to the string-based `term` on `TermLexicon`. 

`frequency` represents how many times a given `term` appears within a document.

`context` is a foreign key to the `Document` model that links each term within a document to its parent document.

## <a name="scraper">`indexer.scraper`</a>
### File name: `indexer/scrape.py`

`scrape.scrape` takes a parameter `url` that indicates the URL of the page to be scraped. It requests the page using the Python `requests` library and first checks the request's status code. If the page returns anything other than status code `200` the module returns a tuple with the first element containing `False` and the second element containing a dict with a single key `status_code` keyed to the returned status code.

If the request was successful, the page's HTML is parsed using the `BeautifulSoup` library. Script and style tags are first removed from the `BeautifulSoup` object before the page's remaining text is retrieved and passed into a helper function `get_full_page_text` that separates each line of text into a tuple of stripped lines that are then split on spaces into chunks. These chunks are then rejoined into a string on their newline characters before the newline characters are removed.

Finally, the cleaned page text is passed into a helper function that splits the page text into a list of words. A tuple is returned from the `scrape` module with the first element True and the second element containing a dictionary of the word list, the page's cleaned full text, and the page's `title` tag.

## <a name="index">`indexer.index`</a>
### File name: `indexer/index.py`

`index` is called with four parameters: `word_list`, `page_title`, `page_url`, `page_full_text`. `word_list` is a list of words scraped from a web page that contains only text. `page_full_text` is a string contains the same content as `word_list` but its structure is maintained for display purposes on retrieval. 

The foundation of this module is a `ParsedDocument` class that handles pre-processing of a list of words from a document to be indexed. This object takes a `word_list` as a parameter and puts each word from that list into lower case. The goal  is to build a list of unique words and a dictionary mapping each unique word to its frequency within the input list of words.
We first determine whether a word is not a stopword (NLTK) and contains only alphabetic characters. If these two conditions are true, the word is then stemmed using NLTK's `SnowballStemmer`. If the stemmed word is not already present in the unique word list, it is added to that list and the stemmed word is initialized in the dictionary to 1. If the stemmed word is already present in the unique word list, we increment its value in the dictionary.

Next, the system determines whether a `Document` given by URL is already present in the system. If it is, the object's fields are updated and saved and we flag it for cleanup. If the `Document` is not present in the system, we create it. 

If the document was flagged for cleanup, we retrieve each `DocumentLexicon` instance that is foreign keyed to that document and decrement its linked `TermLexicon` instance by `DocumentLexicon`.`frequency`. Each `DocumentLexicon` instance is then deleted. 

The `ParsedDocument` and `Document` instances are then passed into a `index_document` function. For each term and frequency in the `ParsedDocument` term frequency map, a corresponding `TermLexicon` entry is queried. If it is found, its frequency is incremented. If it is not found, its frequency is initialized to the frequency in the term frequency map. 

We then query each term within the `DocumentLexicon` and raise an error if we find an entry, as the `DocumentLexicon` should be clear at this point and should never contain duplicated terms. Otherwise we initialize a `DocumentLexicon` entry to the term and frequency within the term frequency map and pass it the `Document` instance that was passed into the function as `context`.

The document is now indexed.


## <a name="retrieval">`indexer.retrieve`</a>
### File name: `indexer/retrieve.py`

`indexer`.`retrieve` takes a string parameter that holds the input query created by user. It first parses the input query into a list of stemmed words after removal of stop words. It then queries the backend database which stores the indexed documents information for term frequency and its context.

The implemented retrieval logic calculates the TF-IDF with smoothed TF and IDF transformations for the input query as well as all documents in the corpus, using information retrieved from the index database. It then calculates the cosine similarity score between the input query and each document based on their TF-IDF values.

Finally, a ranked dictionary is returned with the document IDs as keys, similarity score as values, ranked from the highest similarity score to the lowest for all documents in the corpus.

# (3) Project Set Up 
Clone this repo to where you will work on it:
```sh
git clone https://github.com/styloooo/CourseProject.git
```

All of these commands are issued from the project's top directory that has `manage.py` in it.

Create a virtual environment for the project (I highly recommend [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)).

Install the project dependencies and remember to do so every time you pull the repo. From the top project directory:
```sh
pip install -r requirements.txt
```

Generate a Django secret key:
```sh
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
With your newly created virtual environment activated, open this text file: `$VIRTUAL_ENV/bin/postactivate` and add the value generated by the previous command to the environmental variable `DJANGO_SECRET_KEY`:

```sh
export DJANGO_SECRET_KEY='secret-key-that-you-just-generated'
```

Save the file and check that the environmental variable has been exported - if not, reopen your virtual environment and check again. 

If you are not using a virtual environment or do not plan on committing code, you may open `saveit/settings.py` and set the `SECRET_KEY` variable to a string literal of the key generated above.

If you run into permissions issues with any of the following commands, you need to change the permissions on each of these shell files to make them executable as such:

```sh
chmod +x shell_file_name.sh
```

Finally, push the database migrations:
```sh
./bin/makemigrations.sh
./bin/migrate.sh
```

Download the required NLTK corpora (you only need to do this once per configuration):
```sh
./bin/setup_nltk.sh
```

If the above command does not work, open the Python interpreter with which you will run Django and enter the following:

```py
from nltk import download
download('stopwords')
```

Run the app:
```sh
./bin/runserver.sh
```

## Testing
To run tests from the command line (with default verbosity & all tests):

```sh
python manage.py test
```

This repo includes coverage testing dependencies for determining what lines in a module have been executed by tests. When executed from the project root, this command runs all project tests, generates a coverage report, and opens that report in a browser:

```sh
coverage run manage.py test indexer -v 2 && coverage html && open htmlcov/index.html
```

For more information on configuring Coverage.py, check the docs [here](https://coverage.readthedocs.io/en/6.1.2/).

# (4) Team Member Contributions
## Tyler Davis (tadavis2)
* Drafted proposal & integrated feedback 
* Set up project task assignments and asked group members to pick task(s) (11/7/21)
* Assigned to implement module: [index](#index)
* Assigned to implement database [models](#models) / project setup
* Initial Django project configuration
* Defined database models
* Implemented module: [index](#index)
* Implemented module: [scraper](#scraper)
* Implemented frontend

## Kee Dong (yuqingd2)
* Provided proposal input
* Assigned to implement module: [retrieval](#retrieval)
* Implemented module: [retrieval](#retrieval)
    * Please note that Tyler pushed the commits for this module on Kee's behalf
    * Kee authored this module and its tests but was unable to push it to Git at the time due to travel / time constraints
* Lead on presentation draft

## Mukund Mudhusdan (mukundm2)
* Provided proposal input
* Assigned to implement module: [scraper](#scraper)
* No deliverable
