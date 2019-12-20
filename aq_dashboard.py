
"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
import openaq
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)

api = openaq.OpenAQ()

@APP.route('/')
def root():
    """Base view."""
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    res = []
    for result in body['results']:
        res.append((result['date']['utc'], result['value']))
    return str(res)

@APP.route('/risky')
def risky():
    records = Record.query.filter(Record.value >= 10).all()
    res = []
    for record in records:
        res.append((record.datetime, record.value))
    return str(res)


APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '<Record {}>'.format(self.datetime)


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    for result in body['results']:
        record = Record(datetime=result['date']['utc'], value=result['value'])
        DB.session.add(record)
    DB.session.commit()
    return 'Data refreshed!'
