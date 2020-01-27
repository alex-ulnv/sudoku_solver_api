import datetime

from sudoku_solver_api import db

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


ADMIN_USER_NAME = 'admin'   # IMPORTANT: if the admin username is changed, remove the database file!
ADMIN_PASSWORD = '12345'    # but, can easily change the password before each start :-)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


class Sudoku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    # the field size is set to the output length for 9x9 Sudoku, when the 2-D list is converted to a string
    input = db.Column(db.String(261))
    solution = db.Column(db.String(261))


def admin_exists():
    admin = User.query.filter_by(name=ADMIN_USER_NAME).first()
    if admin:
        return True
    else:
        return False


def create_admin():
    admin = User(
        name=ADMIN_USER_NAME,
        password=generate_password_hash(ADMIN_PASSWORD, method='sha256'),
        admin=True
    )
    db.session.add(admin)
    db.session.commit()


def update_admin_password():
    admin = User.query.filter_by(name=ADMIN_USER_NAME).first()
    if check_password_hash(admin.password, ADMIN_PASSWORD):
        admin.password = generate_password_hash(ADMIN_PASSWORD, method='sha256')
        db.session.commit()


def init_db():
    print('creating tables')
    db.create_all()
    if not admin_exists():
        create_admin()
    else:
        update_admin_password()


if __name__ == '__main__':
    init_db()
