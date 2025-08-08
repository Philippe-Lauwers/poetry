import re

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from .authentication import register
from ..dbModel import User

auth_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@auth_bp.route('/login', methods=['POST'])
def login():
    # Retrieve JSON data from the request
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip().lower()  # could be username or email
    pw = data.get('password', '')

    # 1) Find by email OR username
    user = User.query.filter(or_(
                User.name == identifier,
                User.email == identifier)).first()

    if not user or not user.check_password(pw):
        return jsonify({"login": {"status": False,"message": "Your username/email or password is incorrect" } }), 401
    login_user(user, remember=data.get('remember', False))
    # Flask-Login sets the session cookie
    return jsonify({"login": {"status": True}})

@auth_bp.route('/whoami', methods=['GET'])
@login_required
def whoami():
    u = current_user
    return jsonify({
      "user": {"id": u.id, "name": u.name, "email": u.email}
    })

@auth_bp.route('/registerSave', methods=['POST'])
def register_save():
    # Retrieve JSON data from the request
    data = request.get_json() or {}
    user=data.get('user', None)
    password=data.get('password', None)
    confirm_password=data.get('confirm_password', None)
    email=data.get('email', None)
    gdprConsent = data.get('gdprConsent', None)

    if gdprConsent is None:
        return jsonify({"register":{"status":False,"message": "GDPR consent is required"}}), 400
    if user is None or password is None or confirm_password is None or email is None:
        return jsonify({"register":{"status":False,"message": "Please fill out the required fields"}}), 400
    if password != confirm_password:
        return jsonify({"register":{"status":False,"message": "Passwords do not match"}}), 400
    if not EMAIL_REGEX.match(data['email']):
        return jsonify({'register': {'status': False, 'message': "Please enter a valid email address."}})
    status=register(data)
    return jsonify({"register": status}), 201

@auth_bp.route('/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Logged out"})
