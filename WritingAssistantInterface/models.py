from flask_login import UserMixin

class RemoteUser(UserMixin):
    def __init__(self, user_id, name=None, email=None):
        self.id    = str(user_id)   # must be a string
        self.name  = name
        self.email = email
