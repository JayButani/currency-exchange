from flask_sqlalchemy import model
from . import db
from flask_login import UserMixin
from sqlalchemy.orm import validates
import datetime, string, random, requests

TXN_MESSAGES = dict(
    ADD='Money added to Wallet',
    WITHDRAW='Money withdrawn from Wallet',
    PAID_TO='Money transfer to',
    RECEIVED_FROM='Money received from'
)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
class Helper():

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def get_float_string(amount):
        return "{:.2f}".format(float(amount))

    def convertMoney(from_currency, to_currency, amount):
        url = f'https://openexchangerates.org/api/latest.json?app_id={"c45854a9d2ba49bf93fc9a482302b758"}&base={from_currency}&symbols={to_currency}'
        res = requests.get(url)
        resJson = res.json()
        exchange_rate = resJson['rates'][to_currency]
        converted_amount = exchange_rate * float(amount)
        return {'converted_amount': Helper.get_float_string(converted_amount), 'exchange_rate': exchange_rate}


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

    @staticmethod
    def create(user, base_currency='INR'):
        new_wallet = Wallet(user_id= user.id, currency=base_currency, current_balance=0)
        db.session.add(new_wallet)
        db.session.commit()
        return new_wallet

    @classmethod
    def update(self, amount=None, base_currency=None):
        if amount:
            self.current_balance = self.current_balance + float(amount)
            self.current_balance = Helper.get_float_string(self.current_balance)

        if not self.currency == base_currency:
            self.currency = base_currency
        db.session.commit()

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
    exchange_rate = db.Column(db.Float)

    @validates('status', 'type', 'tag')
    def convert_upper(self, key, value):
        return value.upper()

    def __init__(self, wallet_id, type, original_amount, original_currency, status, tag, description):
        self.wallet_id = wallet_id
        self.txn_id = Transaction.generate_txn_id()
        self.type = type
        self.original_amount = original_amount
        self.original_currency = original_currency
        self.datetime = datetime.datetime.now(),
        self.status = status
        self.tag = tag
        self.description = description

    @staticmethod
    def get_description(tag, sender_receiver):
        if sender_receiver:
            return f'{TXN_MESSAGES[tag.upper()]} {sender_receiver.name}'
        else:
            return TXN_MESSAGES[tag.upper()]

    @staticmethod
    def generate_txn_id(n = 10):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))

    @staticmethod
    def create(wallet, type, amount, currency, tag, user=None):
        transaction = Transaction(
            wallet_id = wallet.id,
            type = type,
            original_amount = amount,
            original_currency = currency,
            tag = tag,
            status = "success",
            description = Transaction.get_description(tag, user)
        )

        if not wallet.currency == currency:
            convertedObj = Helper.convertMoney(currency, wallet.currency, amount)
            transaction.converted_amount = convertedObj['converted_amount']
            transaction.converted_currency = wallet.currency
            transaction.exchange_rate = convertedObj['exchange_rate']

        db.session.add(transaction)
        db.session.commit()
        return transaction

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

    @staticmethod
    def get_currencies():
        all_currencies = Currency.query.all()
        return [[x.code, x.name] for x in all_currencies]