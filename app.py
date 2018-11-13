import os
import sqlite3
from flask import Flask, request, g, jsonify, make_response
import db

app = Flask(__name__)
app.config.from_object(__name__)  # load config from this file , app.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'app.db'),
    SECRET_KEY='development key',
    USERNAME='jonahe',
    PASSWORD='Sneakers123'
))
app.config.from_envvar('APP_SETTINGS', silent=True)


# Connects to database file specified in config
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row  # uses namedtuple object
    return rv


# Open a new database connection if the current context doesn't have one
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# Initializes database using SQL schema provided in root directory
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


# Allows initialization of the database through command line
@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


# Closes the database connection at the end of every request
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# Makes 404 error response return JSON
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# Conducts SQL query on current database
def query_db(query, args=(), one=False):
    # From SQLite 3 with Flask tutorial
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def edit_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()


@app.route('/factory/pens', methods=['POST'])
def post_pen():
    try:
        db.create_pen(request.form['color'], request.form['material'])
        return make_response(jsonify({'success': 'Request ok'}), 200)
    except (TypeError, ValueError, KeyError):
        return make_response(jsonify({'error': 'Bad request'}), 400)


# TODO prevent duplication if same part PUT to server twice
@app.route('/factory/<int:pen_id>/parts', methods=['PUT', 'DELETE'])
def edit_part(pen_id):
    try:
        if request.method == 'PUT':
            db.create_part(request.form['part_name'], pen_id)
        else:
            part = db.get_part_by_name(request.form['part_name'], pen_id)
            db.remove_part(part['id'])
        return make_response(jsonify({'success': 'Request ok'}), 200)
    except (TypeError, ValueError, KeyError):
        return make_response(jsonify({'error': 'Bad request'}), 400)


# TODO prevent duplication if same edge PUT to server twice
@app.route('/factory/<int:pen_id>/assemblies', methods=['PUT', 'DELETE'])
def edit_edge(pen_id):
    try:
        from_node_id = db.get_part_by_name(request.form['parent_part'], pen_id)['id']
        to_node_id = db.get_part_by_name(request.form['child_part'], pen_id)['id']
        if request.method == 'PUT':
            db.add_edge(from_node_id, to_node_id, pen_id)
        else:
            db.remove_edge(from_node_id, to_node_id)
        return make_response(jsonify({'success': 'Request ok'}), 200)
    except (TypeError, ValueError, KeyError):
        return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route('/factory/<int:pen_id>/parts', methods=['GET'])
def get_part(pen_id):
    try:
        all = bool(int(request.args['all']))
        node_id = None
        if 'part_name' in request.args:
            node_id = db.get_part_by_name(request.args['part_name'], pen_id)['id']
        parts = db.get_part(node_id, all, pen_id)
        if all:
            return make_response(jsonify([dict(part) for part in parts]), 200)
        else:
            return make_response(jsonify(dict(parts)) if parts else None, 200)
    except (TypeError, ValueError, KeyError):
        return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route('/factory/<int:pen_id>/parts/advanced', methods=['GET'])
def get_parts_advanced(pen_id):
    try:
        children = request.args['direction'] == 'children'
        parents = request.args['direction'] == 'parents'
        full_assembly = bool(int(request.args['full_assembly']))
        part_name = request.args['part_name']
        node_id = db.get_part_by_name(part_name, pen_id)['id']
        if children and not full_assembly:
            parts = db.get_first_level_children(node_id)
        elif children:
            parts = db.get_all_assembly_parts(node_id)
        elif parents:
            parts = db.get_parent_assemblies(node_id)
        return make_response(jsonify([dict(part) for part in parts]), 200)
    except (TypeError, ValueError, KeyError):
        return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route('/factory/<int:pen_id>/assemblies', methods=['GET'])
def get_assembly(pen_id):
    try:
        has_children = bool(int(request.args['children']))
        has_parents = bool(int(request.args['parents'])) if ('parents' in request.args) else None
        parts = db.get_assembly_subset(pen_id, has_children, has_parents)
        return make_response(jsonify([dict(part) for part in parts]), 200)
    except (TypeError, ValueError, KeyError):
        return make_response(jsonify({'error': 'Bad request'}), 400)


if __name__ == '__main__':
    app.run()
