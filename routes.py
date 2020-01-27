from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
import datetime
from functools import wraps

from sudoku_solver_api import app
from sudoku_solver_api import db
from .models import User
from .models import Sudoku
from .settings import AUTH_TOKEN_EXPIRATION_TIME_MINUTES
from .settings import DELETE_HISTORY_WHEN_USER_IS_DELETED
from .sudoku_solver import SudokuSolver

# Authorization

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(name=data['user_name']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/user/login')
def login():
    auth = request.authorization

    response_fail = make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if not auth or not auth.username or not auth.password:
        return response_fail

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return response_fail

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({
            'user_name' : user.name,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=AUTH_TOKEN_EXPIRATION_TIME_MINUTES)
        }, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})

    return response_fail

# User operations

@app.route('/user/register', methods=['POST'])
def create_user():
    data = request.get_json()
    print(request)
    hashed_password = generate_password_hash(data['password'], method='sha256')

    # Check if the user with the same name already exists
    user = User.query.filter_by(name=data['name']).first()
    if user:
        return jsonify({'message' : 'Cannot create user `{}`: this user name already exists.'.format(data['name'])})

    # Create a new user
    new_user = User(name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'User `{}` was created.'.format(new_user.name)})


@app.route('/user/delete/<user_name>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_name):
    if current_user.name != user_name and not current_user.admin:
        return jsonify({
            'message' : 'Cannot perform this function: only admins can delete other user accounts.'
        })

    user = User.query.filter_by(name=user_name).first()
    if not user:
        return jsonify({'message' : 'No user found!'})

    # Remove user history if specified
    if DELETE_HISTORY_WHEN_USER_IS_DELETED:
        Sudoku.query.filter_by(user_id=user.id).delete()
        db.session.commit()

    # Finally, delete the user
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message' : 'User `{}` was deleted.'.format(user.name)})


@app.route('/user/promote/<user_name>', methods=['PUT'])
@token_required
def promote_user(current_user, user_name):
    # Ensure the current user has the right access level
    if not current_user.admin:
        return jsonify({'message' : 'Cannot promote: you must be admin to promote.'})

    # Locate the user in the database
    user = User.query.filter_by(name=user_name).first()
    if not user:
        return jsonify({'message' : 'No user found!'})

    # Promotion
    user.admin = True
    db.session.commit()

    return jsonify({'message' : '`{}` is now an admin!'.format(user_name)})

@app.route('/user/demote/<user_name>', methods=['PUT'])
@token_required
def demote_user(current_user, user_name):
    # Ensure the current user has the right access level
    if not current_user.admin:
        return jsonify({'message' : 'Cannot promote: you must be admin to promote.'})

    # Locate the user in the database
    user = User.query.filter_by(name=user_name).first()
    if not user:
        return jsonify({'message' : 'No user found!'})

    # Demotion
    user.admin = False
    db.session.commit()

    return jsonify({'message' : '`{}` is not admin anymore!'.format(user_name)})

# General

@app.route('/sudoku', methods=['POST'])
@token_required
def solve_sudoku(current_user):

    # Validate the input
    try:
        data = request.get_json()
    except:
        return jsonify({'message' : 'Cannot parse Sudoku board.'})

    sudoku = SudokuSolver(data)
    sudoku.solve()

    new_sudoku = Sudoku(
        user_id=current_user.id,
        input=sudoku.get_str_input(),
        solution=sudoku.get_str_solution()
    )

    db.session.add(new_sudoku)
    db.session.commit()

    return jsonify(sudoku.get_solution())


@app.route('/history', methods=['POST'])
@token_required
def show_user_sudokus(current_user):

    sudokus = Sudoku.query.filter_by(user_id=current_user.id).all()

    output = []

    for sudoku in sudokus:
        new_sudoku = {}
        new_sudoku['timestamp'] = sudoku.timestamp
        new_sudoku['sudoku'] = json.loads(sudoku.input)
        new_sudoku['sudoku_solved'] = json.loads(sudoku.solution)
        output.append(new_sudoku)

    return jsonify(output)

@app.route('/history_all', methods=['POST'])
@token_required
def show_all_sudokus(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'Only admin can view the whole history!'})

    sudokus = Sudoku.query.all()

    output = []

    for sudoku in sudokus:
        new_sudoku = {}
        new_sudoku['timestamp'] = sudoku.timestamp
        new_sudoku['sudoku'] = json.loads(sudoku.input)
        new_sudoku['sudoku_solved'] = json.loads(sudoku.solution)
        output.append(new_sudoku)

    return jsonify(output)
