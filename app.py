from flask_restful import Resource, Api
import os
import sqlite3
from flask import Flask, request, session, g, abort, jsonify, make_response

app = Flask(__name__)
app.config.from_object(__name__)  # load config from this file , app.py
api = Api(app)

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

def update_db(query, args=()):
    conn = get_db().cursor()
    conn.execute(query, args)
    conn.commit()
    conn.close()

# Serves index.html file to homepage get request
@app.route('/', methods=['GET'])
def show_form():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run()
