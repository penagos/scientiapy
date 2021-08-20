# Scientiapy
An open source community Q&A website written in Python 3 using the Django framework.

[Live Demo](https://scientiapy.penagos.co).

## Features
* Written in Python 3 on a modern framework (Django)
* Small data model
* Responsive (bootstrap) layout
* Allows commenting on questions and answers
* Upvoting of questions and answers
* User notification lists for new questions, comments and answers (email based)
* Ability to tag questions
* Leverages Django admin panel
* Full markdown support
* Basic question search functionality
* Supports search as you type with dropdown results

## Installation
You will need the following packages:
```
sudo apt-get install python3-dev libmysqlclient-dev
```

If you are on CentOS, you can use:
```
sudo yum install mariadb-devel gcc python36u-devel
```

Note you need to be using Python 3 and Pip 3. You can install all PiP dependencies with the following command (issued in the project root):
```
pip install -r requirements.txt
```

To build the database needed by Scientiapy, you will need to run the commands below. Note: the default Scientiapy configuration ships with the MySQL backend (this requires you have access to a MySQL server). If you would like to use a different database backend, you can modify the `settings.py` file (such as SQLITE).
```
python manage.py makemigrations
python manage.py migrate
```

Lastly, to start the development server locally:
```
python manage.py runserver
```

If you wish to bind the server to a an IP other than `127.0.0.1` and the port `8000` you can explicitly pass them to the `runserver` command as:

```
python manage.py runserver IP:PORT
```

## Production Hosting

### Shared installation instructions
```
python3.6 -m venv /path/to/venv
source /path/to/venv/bin/activate
pip3 install -r requirements
```

### CentOS installation instructions
```
sudo yum install httpd-devel
python3.6 -m pip install mod_wsgi
```

You can host this application using the WSGI Apache mod. First ensure you have the mod enabled in `httpd.conf`. To enable such mod, you can run `sudo a2enmod wsgi`. If you do not have the mod installed, you can install it with `sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3`.

Assuming use of a apache virtualhost, you can use something like:
```
<VirtualHost *:80>
  ServerName YourServerName
	DocumentRoot /path/to/scientiapy
  ErrorLog /path/to/errors.log

  <Directory /path/to/scientiapy>
      <Files wsgi.py>
          Require all granted
      </Files>
  </Directory>

  Alias /static/ /path/to/scientiapy/static/
  Alias /static/admin /path/to/scientiapy/static/
    
  <Directory /path/to/scientiapy/static> 
      Order allow,deny
      Allow from all
  </Directory> 

  WSGIDaemonProcess scientiapy python-path=/path/to/scientiapy:/path/to/scientiapy/venv/lib/python3.6/site-packages
  WSGIProcessGroup scientiapy
  WSGIScriptAlias / /path/to/scientiapy/scientiapy/wsgi.py
</VirtualHost>
```
Note this assumes that a virtual environment has been setup (with Python 3.6). The configuration above should be easily adaptable to other server configurations.

## Troubleshooting

**Invalid command 'WSGIDaemonProcess'**

Make sure you have installed the `mod_wsgi` apache extension and enabled it with `sudo a2enmod wsgi`.


## Acknowledgements
Scientiapy makes use of the resources listed below, in no particular order:

* https://github.com/Nodws/bootstrap4-tagsinput
* https://github.com/js-cookie/js-cookie/
* https://www.bootstraptoggle.com
* https://github.com/leemunroe/responsive-html-email-template
* https://highlightjs.org/
* https://github.com/twitter/typeahead.js/