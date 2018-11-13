Sila Nanotechnologies Coding Challenge:
============================

Problem
-------
The task was to create a JSON-based REST API to create, update, delete and query
bills of materials. This application implements all of the following
functionality:

- create a new part
- add one or more parts as "children" to a "parent" part, which then becomes an assembly
- remove one or more parts from an assembly
- delete a part (thereby also deleting the part from its parent assemblies)
- list all parts
- list all assemblies
- list all top level assemblies (assemblies that are not children of another assembly)
- list all subassemblies (assemblies that are children of another assembly)
- list all component parts (parts that are not subassemblies, but are included in a parent assembly)
- list all orphan parts (parts with neither parents nor children)
- list all the first-level children of a specific assembly
- list all parts in a specific assembly
- list all assemblies that contain a specific child part, either directly or indirectly (via a subassembly)

Solution
--------
The solution is a web app built a Flask (Python) server and a sqlite3 database.
It features graph-style database architecture and recursive graph query
functionality.

The routing and application bootstrapping is contained in `app.py`, while the
sql query functionality is contained in `db.py`. The database schema is house in
`schema.sql`.

Very little boilerplate was used, but the database connection functions in
app.py are very standard and do not contain original code: init_db,
get_db, query_db, close_db.

My Level of Experience
----------------------
Before this challenge, I'd never done any front-end or back-end web development.
I had a good deal of experience in Python, but none in Flask or React/JavaScript
(so I learned them both in the process, as well as general networking
knowledge).

Local Installation Instructions
-------------------------------

**This app can be launched from any Mac or Linux computer**

1. Clone the repository

2. **In terminal at home folder:**

  * pip install flask

3. **cd into the repository root directory**

  * export FLASK_APP=app.py
  * python app.py
  * ^C (to shut down server)

  * to initialize the database (clears existing one):
    * flask initdb

  * to run the server on a local port:
    * flask run
  * to run an externally visible server:
    * flask run --host=0.0.0.0

Documentation
-------------
Follow this link https://documenter.getpostman.com/view/5867559/RzZAke7X to
access Postman documentation and download the entire REST API collection
