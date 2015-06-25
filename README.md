##Flask-Angular-Blog

a fun little blog with a Flask backend and AngularJs frontend.
try out the [demo app](https://phlaskr.herokuapp.com) on heroku

####TravisCI Build Status
---
[![Build Status](https://travis-ci.org/jstacoder/flask-angular-blog.svg?branch=master)](https://travis-ci.org/jstacoder/flask-angular-blog)

to use, first install everything in a virtualenv:
```bash
virtualenv venv
. ./venv/bin/activate
pip install -I -r requirements.txt
```
then, just create a file called `local_settings.py` and just add a class for your sensitive settings ie:

```python
class LocalConfig(object):
    SECRET_KEY = 'somesecret'
    DATABASE_URI = 'sqlite:///test.db
```

then run 
```bash
python phlaskr/seed_db.py
```

then, (as long as you installed everything inside of a virtualenv) 
to run it just:

```bash
honcho start
```

