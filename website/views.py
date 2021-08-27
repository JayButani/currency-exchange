from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from . import db
from .models import Transaction, User, Wallet, Currency
import os, datetime, string, random
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
        file.save(os.path.join(current_app.root_path + '/static/uploads/', filename))
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
    if wallet:
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

        create_txn(wallet=wallet, type='CR', amount=amount, currency=currency, tag='add')
        update_wallet(wallet, amount, wallet.currency)
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

        create_txn(wallet=wallet, type='DR', amount=amount, currency=wallet.currency, tag='withdraw')
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
        receiver_user = User.query.filter_by(id = receiver_id).first()
        receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()
        # sender entry
        create_txn(wallet=sender_wallet, type='DR', amount=amount, currency=sender_wallet.currency, tag='PAID_TO', user=receiver_user)
        update_wallet(sender_wallet, -abs(float(amount)), sender_wallet.currency)

        # receiver entry
        sender_user = User.query.filter_by(id = current_user.id).first()
        create_txn(wallet=receiver_wallet, type='CR', amount=amount, currency=receiver_wallet.currency, tag='RECEIVED_FROM', user=sender_user)
        update_wallet(receiver_wallet, float(amount), receiver_wallet.currency)

        flash('Your money transferred successfully!', category='success')
        return redirect(url_for('views.wallet'))
    else:
        all_users = User.query.filter(User.id != current_user.id)
        return render_template("wallet_transfer.html", user=current_user, wallet=wallet, all_users=all_users)

def create_wallet(user, base_currency):
    new_wallet = Wallet(user_id= user.id, currency= base_currency, current_balance=0)
    db.session.add(new_wallet)
    db.session.commit()
    return new_wallet

def update_wallet(wallet, amount=None, base_currency=None):
    if amount:
        wallet.current_balance = wallet.current_balance + float(amount)

    if not wallet.currency == base_currency:
        wallet.currency = base_currency
        #TODO: do balance conversion before updating wallet currency
    db.session.commit()

def generate_txn_id(n = 10):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))

def create_txn(wallet, type, amount, currency, tag, user=None):
    if not wallet.currency == currency:
        pass

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
