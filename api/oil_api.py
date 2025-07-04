import os
import flask
from flask import jsonify, request
from flask import make_response
from project.data import db_session
from project.main import app
from project.data.oil import Oil

blueprint = flask.Blueprint(
    'oil_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/oil')
def get_oil():
    db_sess = db_session.create_session()
    oil = db_sess.query(Oil).all()
    return jsonify(
        {
            'oil':
                [item.to_dict(only=('title', 'coo'))
                 for item in oil]
        }
    )


@blueprint.route('/api/oil/<int:oil_id>', methods=['GET'])
def get_oil(oil_id):
    db_sess = db_session.create_session()
    oil = db_sess.query(Oil).get(oil_id)
    if not oil:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'oil': oil.to_dict(only=(
                'title', 'coo'))
        }
    )


@blueprint.route('/api/oil/', methods=['POST'])
def add_oil():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['title', 'coo']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    oil = Oil(
        title=request.json['title'],
        coo=request.json['coo'],
    )
    db_sess.add(oil)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/oil/<int:oil_id>', methods=['DELETE'])
def delete_oil(oil_id):
    db_sess = db_session.create_session()
    oil = db_sess.query(Oil).get(oil_id)
    if not oil:
        return jsonify({'error': 'Not found'})
    db_sess.delete(oil)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/oil/<int:oil_id>', methods=['POST'])
def update_oil(oil_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'coo']):
        return jsonify({'error': 'Bad request'})
    oil = Oil(
        id=oil_id,
        title=request.json['title'],
        coo=request.json['coo']
    )
    oil_to_update = db_sess.query(Oil).filter(Oil.id == oil_id).first()
    if not oil_to_update:
        return jsonify({'error': 'Not found'})
    if oil_to_update:
        oil_to_update.id = oil.id
        oil_to_update.title = oil.title
        oil_to_update.coo = oil.coo
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/books/load/<int:oil_id>', methods=['GET'])
def load_oil(oil_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    oil_to_load = db_sess.query(Oil.title).filter(Oil.id == oil_id).first()[0]
    homeDir = os.path.expanduser("~")
    try:
        file = open('storage/{}'.format(oil_to_load), "rb")
        f = open('{}/{}'.format(homeDir, oil_to_load), "wb")
        f.write(file.read())
        f.close()
    except FileNotFoundError:
        return jsonify({'error': 'no such file "{}"'.format(oil_to_load)})
    return jsonify({'success': 'save in {}/{}'.format(homeDir, oil_to_load)})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
