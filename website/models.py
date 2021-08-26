from flask_sqlalchemy import model
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import validates

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    profile_image_url = db.Column(db.String(200), nullable=True)

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    currency = db.Column(db.String(4), nullable=False)
    current_balance = db.Column(db.Float, nullable=False, default=0.0)

    @validates('currency')
    def convert_upper(self, key, value):
        return value.upper()

    def __init__(self, user_id, currency, current_balance):
        self.user_id = user_id
        self.currency = currency
        self.current_balance = current_balance

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    txn_id = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    original_amount = db.Column(db.Float, nullable=False)
    original_currency = db.Column(db.String(4), nullable=False)
    converted_amount = db.Column(db.Float)
    converted_currency = db.Column(db.String(4))
    description = db.Column(db.String(200))
    tag = db.Column(db.String(50))
    datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)

    @validates('status', 'type', 'tag')
    def convert_upper(self, key, value):
        return value.upper()

    def __init__(self, wallet_id, txn_id, type, original_amount, original_currency, datetime, status, tag, description):
        self.wallet_id = wallet_id
        self.txn_id = txn_id
        self.type = type
        self.original_amount = original_amount
        self.original_currency = original_currency
        self.datetime = datetime
        self.status = status
        self.tag = tag
        self.description = description

class Currency(db.Model):
    __tablename__ = 'currencies'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False)
    name = db.Column(db.String(200))

    @validates('code')
    def convert_upper(self, key, value):
        return value.upper()

    def __init__(self, code, name):
        self.code = code
        self.name = name