from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from ..dbModel import User
from ..extensions import db

auth_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')

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

@auth_bp.route('/register', methods=['POST'])
def api_register():
    # Retrieve JSON data from the request
    data = request.get_json() or {}
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already in use"}), 400

    user = User(
      name=data.get('username'),
      email=data.get('email').lower()
    )
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registration successful"}), 201

@auth_bp.route('/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Logged out"})
