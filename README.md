# CourseProject

Please fork this repository and paste the github link of your fork on Microsoft CMT. Detailed instructions are on Coursera under Week 1: Course Project Overview/Week 9 Activities.

# Requirements
Project built using Python 3.9.2
Django 3.2.9

# Project Set Up 
Install PostgreSQL if you do not already have it. Enter the Postgres shell and create a new database called `saveit`: 

```sql
CREATE DATABASE saveit;
```

Clone this repo to where you will work on it:
```sh
git clone http://this.repo/url
```

Create a virtual environment for the project (I highly recommend [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)). Configure your environmental variable to point to your local Postgres installation. Using `virtualenvwrapper` you need to open: `$VIRTUAL_ENV/bin/postactivate` and add the following line. Change `psql_user` and `psql_password` to your local PSQL install's username and password:

```sh
export SAVEIT_DB_URL='postgres://psql_user:psql_password@localhost/saveit'
```

Save the file and check that the environmental variable has been exported - if not, reopen your virtual environment and check again. 

Install the project dependencies and remember to do so every time you pull the repo. From the top project directory:
```sh
pip install -r requirements.txt
```

Finally, push the database migrations to Postgres:
```sh
> python manage.py makemigrations
> python manage.py migrate
```

Run the app to see if it launches without error:
```sh
python manage.py runserver
```