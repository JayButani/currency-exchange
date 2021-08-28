from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from . import db, views
from website.models import User, Wallet, Currency, Transaction
from werkzeug.utils import secure_filename
from sqlalchemy import desc

walletView = Blueprint('walletView', __name__)

@walletView.route('/wallet', methods=['GET'])
@login_required
def wallet():
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    if wallet and wallet.currency:
        transactions = Transaction.query.filter_by(wallet_id=wallet.id).order_by(desc(Transaction.datetime))
        return render_template("wallet.html", user=current_user, wallet=wallet, transactions=transactions)
    else:
        flash('Please set your currency to access your Wallet.', category='success')
        return redirect(url_for('views.profile'))

@walletView.route('/wallet/add', methods=['GET', 'POST'])
@login_required
def wallet_add():
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        amount = request.form.get('amount')
        currency = request.form.get('currency')
        
        transaction = Transaction.create(wallet=wallet, type='CR', amount=amount, currency=currency, tag='add')
        wallet.update((transaction.converted_amount or transaction.original_amount), wallet.currency)
        flash('Your transaction is successful. Wallet Balance updated!', category='success')
        return redirect(url_for('walletView.wallet'))
    else:
        return render_template("wallet_add.html", user=current_user, wallet=wallet, all_currencies=Currency.get_currencies())

@walletView.route('/wallet/withdraw', methods=['GET', 'POST'])
@login_required
def wallet_withdraw():
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        amount = request.form.get('amount')

        if wallet.current_balance < float(amount):
            flash('You can\'t withdraw more than your current balance.', category='error')
            return redirect(url_for('walletView.wallet_withdraw'))

        transaction = Transaction.create(wallet=wallet, type='DR', amount=amount, currency=wallet.currency, tag='withdraw')
        wallet.update(-abs(float(amount)), wallet.currency)
        flash('Your withdrawal is successful. Wallet Balance updated!', category='success')
        return redirect(url_for('walletView.wallet'))
    else:
        return render_template("wallet_withdraw.html", user=current_user, wallet=wallet)

@walletView.route('/wallet/transfer', methods=['GET', 'POST'])
@login_required
def wallet_transfer():
    sender_wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        receiver_id = request.form.get('receiver')
        amount = request.form.get('amount')

        if sender_wallet.current_balance < float(amount):
            flash('You can\'t transfer more than your current balance.', category='error')
            return redirect(url_for('walletView.wallet_transfer'))

        receiver_user = User.query.filter_by(id = receiver_id).first()
        # sender entry
        transaction = Transaction.create(wallet=sender_wallet, type='DR', amount=amount, currency=sender_wallet.currency, tag='PAID_TO', user=receiver_user)
        sender_wallet.update(-abs(float((transaction.converted_amount or transaction.original_amount))), sender_wallet.currency)

        # receiver entry
        receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()
        if not receiver_wallet:
            receiver_wallet = Wallet.create(receiver_user)

        sender_user = User.query.filter_by(id = current_user.id).first()
        transaction = Transaction.create(wallet=receiver_wallet, type='CR', amount=amount, currency=sender_wallet.currency, tag='RECEIVED_FROM', user=sender_user)
        receiver_wallet.update((transaction.converted_amount or transaction.original_amount), receiver_wallet.currency)

        flash('Your money transferred successfully!', category='success')
        return redirect(url_for('walletView.wallet'))
    else:
        all_users = User.query.filter(User.id != current_user.id)
        return render_template("wallet_transfer.html", user=current_user, wallet=sender_wallet, all_users=all_users)