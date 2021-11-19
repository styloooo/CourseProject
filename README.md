# CourseProject

Please fork this repository and paste the github link of your fork on Microsoft CMT. Detailed instructions are on Coursera under Week 1: Course Project Overview/Week 9 Activities.

# Requirements
Project built using Python 3.9.2
Django 3.2.9

# Project Set Up 
Install PostgreSQL if you do not already have it. Enter the Postgres shell and create a new database called `saveit`: 

```sql
> CREATE DATABASE saveit;
```

Clone this repo to where you will work on it:
```sh
> git clone http://this.repo/url
```

All of these commands are issued from the project's top directory that has `manage.py` in it.

Create a virtual environment for the project (I highly recommend [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)). Configure your environmental variable to point to your local Postgres installation. Using `virtualenvwrapper` you need to open: `$VIRTUAL_ENV/bin/postactivate` and add the following line. Change `psql_user` and `psql_password` to your local PSQL install's username and password:

```sh
export SAVEIT_DB_URL='postgres://psql_user:psql_password@localhost/saveit'
```

Generate a Django secret key:
```sh
>python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Save the secret key generated here to your environmental variables:
```sh
export DJANGO_SECRET_KEY='secret-key-that-you-just-generated'
```

Save the file and check that the environmental variable has been exported - if not, reopen your virtual environment and check again. 

Install the project dependencies and remember to do so every time you pull the repo. From the top project directory:
```sh
> pip install -r requirements.txt
```

If you run into permissions issues with any of the following commands, you need to change the permissions on each of these shell files to make them executable as such:

```sh
> chmod +x shell_file_name.sh
```

Finally, push the database migrations to Postgres:
```sh
> ./bin/makemigrations.sh
> ./bin/migrate.sh
```

Download the required NLTK corpora (you only need to do this once per configuration):
```sh
./bin/setup_nltk.sh
```

Run the app to see if it launches without error:
```sh
> ./bin/runserver.sh
```

# Testing
To run tests from the command line (with default verbosity & all tests):

```sh
python manage.py test
```

This repo includes coverage testing dependencies for determining what lines in a module have been executed. When executed from the project root, this command runs all project tests, generates a coverage report, and opens that report in a browser:

```sh
coverage run manage.py test indexer -v 2 && coverage html && open htmlcov/index.html
```

For more information on configuring Coverage.py, check the docs [here](https://coverage.readthedocs.io/en/6.1.2/).
