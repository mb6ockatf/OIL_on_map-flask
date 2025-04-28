import os

import flask
from flask import jsonify, request
from flask import make_response
from project.data import db_session
from project.data.users import User
from project.main import app

blueprint = flask.Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/user')
def get_user():
    db_sess = db_session.create_session()
    user = db_sess.query(User).all()
    return jsonify(
        {
            'user':
                [item.to_dict(only=('name', 'right_id'))
                 for item in user]
        }
    )


@blueprint.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'user': user.to_dict(only=(
                'name', 'right_id'))
        }
    )


@blueprint.route('/api/user/', methods=['POST'])
def add_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'user_id']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = User(
        name=request.json['name'],
        login=request.json['login'],
    )
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'login']):
        return jsonify({'error': 'Bad request'})
    user = User(
        id=user_id,
        name=request.json['name'],
        login=request.json['login']
    )
    user_to_update = db_sess.query(User).filter(User.id == user_id).first()
    if not user_to_update:
        return jsonify({'error': 'Not found'})
    if user_to_update:
        user_to_update.id = user.id
        user.name = user.name
        user_to_update.login = user.login
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/load/<int:user_id>', methods=['GET'])
def load_user(user_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    user_to_load = db_sess.query(User.name).filter(User.id == user_id).first()[0]
    homeDir = os.path.expanduser("~")
    try:
        file = open('storage/{}'.format(user_to_load), "rb")
        f = open('{}/{}'.format(homeDir, user_to_load), "wb")
        f.write(file.read())
        f.close()
    except FileNotFoundError:
        return jsonify({'error': 'no such file "{}"'.format(user_to_load)})
    return jsonify({'success': 'save in {}/{}'.format(homeDir, user_to_load)})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
