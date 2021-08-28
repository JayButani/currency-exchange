from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from . import db
from .models import User, Wallet, Currency
import os
from werkzeug.utils import secure_filename

MYDIR = os.path.dirname(__file__)
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
                wallet = Wallet.create(user, base_currency)
            else:
                wallet.update(base_currency=base_currency )

            user.name = name
            db.session.commit()

            flash('Profile has been updated!', category='success')
            return redirect(url_for('views.profile'))

    wallet = Wallet.query.filter_by(user_id= current_user.id).first()
    return render_template("profile.html", user=current_user, wallet=wallet, all_currencies= Currency.get_currencies())

@views.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        response = jsonify({'success':False, 'message': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        response = jsonify({'success':False, 'message': 'No image selected for uploading'})

    if file and Helper.allowed_file(file.filename):
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