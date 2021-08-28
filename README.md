# Currency Exchange

Currency Exchange's user can add money in any currency to his wallet, he can withdraw and transfer to his friends and family using his wallet.
While transfering to friend exchange rate is also apply. ie. you can transfer from your INR wallet to friends USD wallet.

## Feature
- User Login/Signup
- User can update his Profile photo, Name, Default currency,
- User can add money in any currency to his wallet
- User can withdraw from his account
- User can Transfer to any user within system from his account. You can send INR and your friend will get USD.

## Running on Local
### Prerequisite
- Python 3.8
- Postgresql
- Signup on https://openexchangerates.org/ and get the API key for Currecny conversion

## Steps
- Create virtual environment first
    `$ python3 -m venv env`
- Activate your environment
    `$ source env/bin/activate`
- Install pip requirements
    `$ pip install -r requirements.txt`
- Set the environment variable, run below command on terminal
    `$ export FLASK_APP=main.py`
    `$ export FLASK_ENV=development`
- Migrate our database
    `$ flask db init`
    `$ flask db migrate`
    `$ flask db upgrade`
- Start server
   `$ flask run`
- Go to http://127.0.0.1:5000

## Tech
- Flask
- Jinja2
- PostgreSQL
- Twitter Bootstrap
- Docker

## Plugin
- python-dotenv
- flask
- Flask-SQLAlchemy
- flask-login
- Flask-Migrate
- psycopg2-binary
- gunicorn
- pytest
- requests


## License

MIT
**Free Software**
