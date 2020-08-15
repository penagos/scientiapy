# Scientiapy
An open source knowledge sharing website written in Python 3 using the Django framework.

## Installation
You will need the following packages:
```
sudo apt-get install python3-dev libmysqlclient-dev
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

## Features
* Full markdown support
* Tagging questions
* Upvoting questions and answers
* Post comments
* Responsive layout
* Lightweight database
* Small application
* (coming soon) email notifications
