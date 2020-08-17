# Scientiapy
An open source knowledge sharing website written in Python 3 using the Django framework.

## Features
* Written in Python 3 on a modern framework (Django)
* Small data model
* Responsive (bootstrap) layout
* Allows commenting on questions and answers
* Upvoting of questions and answers
* User notification lists for new questions and answers (email based)
* Ability to tag questions
* Leverages Django admin panel
* Full markdown support

## Installation
You will need the following packages:
```
sudo apt-get install python3-dev libmysqlclient-dev
```

If you are on CentOS, you can use:
```
sudo yum install mariadb-devel gcc python36u-devel
```

Then you can install all PiP dependencies with the following command (issued in the project root):
```
pip install -r requirements.txt
```

To build the database needed by Scientiapy, you will need to run:
```
python3.7 manage.py makemigrations
python3.7 manage.py migrate
```

Lastly, to start the development server locally:
```
python3.7 manage.py runserver
```
