from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from . import db
from .models import User
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')

        if len(name) < 2:
            flash('Name must be greater than 2 character.', category='error')
        else:
            user = User.query.filter_by(id=current_user.id).first()
            user.name = name
            db.session.commit()
            flash('Profile has been updated!', category='success')
            return redirect(url_for('views.profile'))

    return render_template("profile.html", user=current_user)


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


@views.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet():
    return render_template("wallet.html", user=current_user)
