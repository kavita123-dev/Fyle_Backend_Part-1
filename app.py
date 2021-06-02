import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from flask_cors import CORS

db_host = os.environ['POSTGRESQL_ADDON_HOST']
db_name = os.environ['POSTGRESQL_ADDON_DB']
db_user = os.environ['POSTGRESQL_ADDON_USER']
db_URI = os.environ['POSTGRESQL_ADDON_URI']
db_password = os.environ['POSTGRESQL_ADDON_PASSWORD']

try:
    conn = psycopg2.connect(
        f"dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}'")
    print("Database connected")
except:
    print("Not able to connect to Database")


def autocomplete(keyword, limit, offset):
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql_query = f'''select
                   *
                   from
                   branches
                   where
                   branch like '%{keyword}%'
                   order by ifsc
                   limit {limit} ; '''
    cursor.execute(sql_query)
    record = cursor.fetchall()

    return record


def getBranch(keyword, limit, offset):
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql_query = f'''
                    select
                *
                from
                branches
                where
                address like '%{keyword}%'
                or branch like '%{keyword}%'
                or city like '%{keyword}%'
                or district like '%{keyword}%'
                or state like '%{keyword}%'
                
                order by
                ifsc
                limit
                {limit} 
                offset {offset};
            '''
    cursor.execute(sql_query)
    record = cursor.fetchall()

    return record


app = Flask(__name__)
CORS(app)
app.config['JSON_SORT_KEYS'] = False


@app.errorhandler(404)
def not_found(e):
    return '''
            <h1>bad request!</h1> 
            Endpoint: /api/branches?q=<>
            Endpoint: /api/branches/autocomplete?q=<>
            ''', 400


@app.route('/api/branches/autocomplete')
def auto_branch():
    search_query = request.args['q']

    try:
        limit = request.args['limit']
    except:
        limit = 5

    try:
        offset = request.args['offset']
    except:
        offset = 0
    data = {}
    data["branches"] = autocomplete(search_query.upper(), limit, offset)

    return jsonify(data)


@app.route('/api/branches')
def branch():
    search_query = request.args['q']

    try:
        limit = request.args['limit']
    except:
        limit = 5

    try:
        offset = request.args['offset']
    except:
        offset = 0
    data = {}
    data["branches"] = getBranch(search_query.upper(), limit, offset)

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
