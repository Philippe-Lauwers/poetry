from ..dbModel import User
from ..extensions import db


def register(data:dict):
    orm_user = db.session.query(User).filter(User.name == data.get('user')).first()
    if orm_user:
        return {"status": False, "message": "Your username already exists in our database."}
    orm_user = db.session.query(User).filter(User.email == data.get('email')).first()
    if orm_user:
        return {"status": False, "message": "Email already exists in our database."}


    orm_user = User(name=data.get('user'), email=data.get('email'))
    orm_user.set_password(data.get('password'))
    db.session.add(orm_user)
    try:
        db.session.commit()
        return {"status": True, "message": "You are registered successfully.<br>Please login."}
    except Exception as e:
        db.session.rollback()
        return {"status": False, "message": str(e)}

    pass