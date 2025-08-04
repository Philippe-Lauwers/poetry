import os
import requests
from dotenv import load_dotenv

from flask import Flask, request, jsonify, make_response, redirect, url_for
from flask_login import LoginManager
from models import RemoteUser  # <— your tiny UserMixin class

load_dotenv()

BASE = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE, 'static'),
    template_folder=os.path.join(BASE, 'templates'),
)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "abcdefghijklmnopqrstuvwxyz012345")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5050")
app.config['BACKEND_URL'] = BACKEND_URL
app.config.update(
    SESSION_COOKIE_SECURE=False,     # allows cookies over HTTP (for local dev)
    SESSION_COOKIE_SAMESITE='Lax',   # works for same-site XHR/fetch
    SESSION_COOKIE_PATH='/'          # ensure it’s sent on all paths
)
# ─── Flask-Login setup ────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "main.login"  # adjust if your login route is named differently
login_manager.login_message_category = "warning"


@login_manager.unauthorized_handler
def unauthorized_callback():
    best_match = request.accept_mimetypes.best_match(
        ['application/json', 'text/html']
    )
    # If JSON is equally or more preferred than HTML:
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            "login": {
                "status": False,
                "message": "Please log in."
            }
        }), 401
    return redirect(url_for('main.login', next=request.path))


# @login_manager.user_loader
# def load_user(user_id):
#     # Proxy the browser’s session cookie to the auth service
#     cookies = request.cookies.to_dict()
#     resp = requests.get(f"{BACKEND_URL}/auth/whoami", cookies=cookies)
#     if resp.ok:
#         u = resp.json().get('user', {})
#         return RemoteUser(u.get('id'), u.get('name'), u.get('email'))
#     return None
# REMOVE or disable this:
@login_manager.user_loader
def load_user(user_id):
    return None

from flask_login import LoginManager, login_user, UserMixin, login_required

# Instead of user_loader
@login_manager.request_loader
def load_user_from_request(request):
    cookies = request.cookies.to_dict()
    resp = requests.get(f"{BACKEND_URL}/auth/whoami", cookies=cookies)
    if resp.ok:
        u = resp.json().get('user', {})
        return RemoteUser(u.get('id'), u.get('name'), u.get('email'))
    return None


# ─── Blueprint registration ───────────────────────
from routes import main_bp

app.register_blueprint(main_bp)

if __name__ == '__main__':
    port = int(os.getenv("INTERFACE_PORT", 5000))
    host = os.getenv("INTERFACE_HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=True, use_reloader=False)
