from django.core.management.base import BaseCommand, CommandError
from nltk import download
from os import environ, path
from platform import system

class Command(BaseCommand):
    help = 'Downloads necessary NLTK corpus files'

    def handle(self, *args, **options):
        NLTK_PACKAGES_TO_INSTALL = (
            'stopwords',
        )

        if 'VIRTUAL_ENV' in environ.keys():
            download_dir = path.join(environ['VIRTUAL_ENV'], 'nltk_data')
        elif system() == 'Darwin':
            download_dir = '/usr/share/nltk_data'
        elif system() == 'Windows':
            download_dir = 'C:/nltk_data'
        elif system() == 'Linux':
            download_dir = '/usr/share/nltk_data'
        else:
            raise RuntimeError("Unrecognized system architecture: can't install nltk_data")

        for package in NLTK_PACKAGES_TO_INSTALL:
            download(package, download_dir=download_dir)
