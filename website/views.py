from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from . import db
from .models import Transaction, User, Wallet, Currency
import os, datetime, string, random, requests
from werkzeug.utils import secure_filename
from sqlalchemy import desc

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
TXN_MESSAGES = dict(
    ADD='Money added to Wallet',
    WITHDRAW='Money withdrawn from Wallet',
    PAID_TO='Money transfer to',
    RECEIVED_FROM='Money received from'
)
views = Blueprint('views', __name__)
MYDIR = os.path.dirname(__file__)

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        base_currency = request.form.get('default_currency')

        if len(name) < 2:
            flash('Name must be greater than 2 character.', category='error')
        else:
            user = User.query.filter_by(id=current_user.id).first()
            wallet = Wallet.query.filter_by(user_id= user.id).first()

            if not wallet:
                wallet = create_wallet(user, base_currency)
            else:
                update_wallet(wallet=wallet, base_currency=base_currency )

            user.name = name
            db.session.commit()

            flash('Profile has been updated!', category='success')
            return redirect(url_for('views.profile'))

    wallet = Wallet.query.filter_by(user_id= current_user.id).first()
    return render_template("profile.html", user=current_user, wallet=wallet, all_currencies=get_currencies())


@views.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        response = jsonify({'success':False, 'message': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        response = jsonify({'success':False, 'message': 'No image selected for uploading'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(MYDIR, 'static','uploads', filename))
        user = User.query.filter_by(id=current_user.id).first()
        profile_image_url = '/static/uploads/' + filename
        user.profile_image_url = profile_image_url
        db.session.commit()
        response = jsonify({'success':True, 'message': 'Image successfully uploaded and displayed below', 'url': profile_image_url})
    else:
        response = jsonify({'success':False, 'message': 'Allowed image types are - png, jpg, jpeg, gif'})
 
    response.status_code = 200
    return response

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/wallet', methods=['GET'])
@login_required
def wallet():
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    if wallet and wallet.currency:
        transactions = Transaction.query.filter_by(wallet_id=wallet.id).order_by(desc(Transaction.datetime))
        return render_template("wallet.html", user=current_user, wallet=wallet, transactions=transactions)
    else:
        flash('Please set your currency to access your Wallet.', category='success')
        return redirect(url_for('views.profile'))


@views.route('/wallet/add', methods=['GET', 'POST'])
@login_required
def wallet_add():
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        amount = request.form.get('amount')
        currency = request.form.get('currency')

        transaction = create_txn(wallet=wallet, type='CR', amount=amount, currency=currency, tag='add')
        update_wallet(wallet, (transaction.converted_amount or transaction.original_amount), wallet.currency)
        flash('Your transaction is successful. Wallet Balance updated!', category='success')
        return redirect(url_for('views.wallet'))
    else:
        return render_template("wallet_add.html", user=current_user, wallet=wallet, all_currencies=get_currencies())


@views.route('/wallet/withdraw', methods=['GET', 'POST'])
@login_required
def wallet_withdraw():
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        amount = request.form.get('amount')

        if wallet.current_balance < float(amount):
            flash('You can\'t withdraw more than your current balance.', category='error')
            return redirect(url_for('views.wallet_withdraw'))

        transaction = create_txn(wallet=wallet, type='DR', amount=amount, currency=wallet.currency, tag='withdraw')
        update_wallet(wallet, -abs(float(amount)), wallet.currency)
        flash('Your withdrawal is successful. Wallet Balance updated!', category='success')
        return redirect(url_for('views.wallet'))
    else:
        return render_template("wallet_withdraw.html", user=current_user, wallet=wallet)

@views.route('/wallet/transfer', methods=['GET', 'POST'])
@login_required
def wallet_transfer():
    sender_wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        receiver_id = request.form.get('receiver')
        amount = request.form.get('amount')

        if sender_wallet.current_balance < float(amount):
            flash('You can\'t transfer more than your current balance.', category='error')
            return redirect(url_for('views.wallet_transfer'))

        receiver_user = User.query.filter_by(id = receiver_id).first()
        receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()
        # sender entry
        transaction = create_txn(wallet=sender_wallet, type='DR', amount=amount, currency=sender_wallet.currency, tag='PAID_TO', user=receiver_user)
        update_wallet(sender_wallet, -abs(float((transaction.converted_amount or transaction.original_amount))), sender_wallet.currency)

        # receiver entry
        sender_user = User.query.filter_by(id = current_user.id).first()
        transaction = create_txn(wallet=receiver_wallet, type='CR', amount=amount, currency=sender_wallet.currency, tag='RECEIVED_FROM', user=sender_user)
        update_wallet(receiver_wallet, (transaction.converted_amount or transaction.original_amount), receiver_wallet.currency)

        flash('Your money transferred successfully!', category='success')
        return redirect(url_for('views.wallet'))
    else:
        all_users = User.query.filter(User.id != current_user.id)
        return render_template("wallet_transfer.html", user=current_user, wallet=sender_wallet, all_users=all_users)

def create_wallet(user, base_currency):
    new_wallet = Wallet(user_id= user.id, currency= base_currency, current_balance=0)
    db.session.add(new_wallet)
    db.session.commit()
    return new_wallet

def update_wallet(wallet, amount=None, base_currency=None):
    if amount:
        wallet.current_balance = wallet.current_balance + float(amount)
        wallet.current_balance = get_float_string(wallet.current_balance)

    if not wallet.currency == base_currency:
        wallet.currency = base_currency
        #TODO: do balance conversion before updating wallet currency
    db.session.commit()

def generate_txn_id(n = 10):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))

def create_txn(wallet, type, amount, currency, tag, user=None):
    transaction = Transaction(
        wallet_id = wallet.id,
        txn_id=generate_txn_id(),
        type=type,
        original_amount=amount,
        original_currency=currency,
        tag=tag,
        datetime=datetime.datetime.now(),
        status="success",
        description=get_description(tag, user)
    )
    
    if not wallet.currency == currency:
        convertedObj = convertMoney(currency, wallet.currency, amount)
        transaction.converted_amount = convertedObj['converted_amount']
        transaction.converted_currency = wallet.currency
        transaction.exchange_rate = convertedObj['exchange_rate']

    db.session.add(transaction)
    db.session.commit()
    return transaction

def get_description(tag, sender_receiver):
    if sender_receiver:
        return f'{TXN_MESSAGES[tag.upper()]} {sender_receiver.name}'
    else:
        return TXN_MESSAGES[tag.upper()]

def get_currencies():
    all_currencies = Currency.query.all()
    return [[x.code, x.name] for x in all_currencies]

def convertMoney(from_currency, to_currency, amount):
    url = f'https://openexchangerates.org/api/latest.json?app_id={"c45854a9d2ba49bf93fc9a482302b758"}&base={from_currency}&symbols={to_currency}'
    res = requests.get(url)
    resJson = res.json()
    exchange_rate = resJson['rates'][to_currency]
    converted_amount = exchange_rate * float(amount)
    return {'converted_amount': get_float_string(converted_amount), 'exchange_rate': exchange_rate}

def get_float_string(amount):
    return "{:.2f}".format(float(amount))