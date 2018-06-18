#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import postgresql
from datetime import datetime
import flask
from flask import request
import json
import uuid

from multiprocessing import Process

from producer import get_friends

app = flask.Flask(__name__)

# disables JSON pretty-printing in flask.jsonify
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


def db_conn():
    pass
    # return postgresql.open('pq://eax@localhost/eax')


def to_json(data):
    return json.dumps(data) + "\n"


def resp(code, data):
    return flask.Response(
        status=code,
        mimetype="application/json",
        response=to_json(data)
    )


def theme_validate():
    errors = []
    json = flask.request.get_json()
    if json is None:
        errors.append(
            "No JSON sent. Did you forget to set Content-Type header" +
            " to application/json?")
        return (None, errors)

    for field_name in ['type', 'query']:
        if type(json.get(field_name)) is not str:
            errors.append(
                "Field '{}' is missing or is not a string".format(
          field_name))

    return (json, errors)


def affected_num_to_code(cnt):
    code = 200
    if cnt == 0:
        code = 404
    return code

# ---------------- error -------------------------------------------

# e.g. failed to parse json
@app.errorhandler(400)
def page_not_found(e):
    return resp(400, {})

@app.errorhandler(404)
def page_not_found(e):
    return resp(400, {})

@app.errorhandler(405)
def page_not_found(e):
    return resp(405, {})

# ---------------- route -------------------------------------------
@app.route('/')
def root():
    return flask.redirect('/api/1.0/query')

# конкретный запрос и его результат
@app.route('/api/1.0/query/<int:query_id>', methods=['GET'])
def get_query(query_id):
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    with db_conn() as db:
        tuples = db.query("SELECT * FROM query WHERE uid = $1")
        queries = []
        for row in tuples(query_id):
            queries.append(row)
        return resp(200, {"queries": queries})

# список всех активных запросов
@app.route('/api/1.0/query', methods=['GET'])
def get_queries():

    offset = request.args.get('offset')
    limit = request.args.get('limit')

    with db_conn() as db:
        tuples = db.query("SELECT uid, q_type, state, dt_start FROM query WHERE state = $1")
        queries = []
        for (uid, q_type, state, dt_start) in tuples('running'):
            queries.append({"id": uid, "type": q_type, "state": state, "dt_start":dt_start})
        return resp(200, {"queries": queries})

# Отдать запрос в парсер и вернуть uid запроса
@app.route('/api/1.0/query', methods=['POST'])
def post_query():

    (json, errors) = theme_validate()
    if errors:  # list is not empty
        return resp(400, {"errors": errors})

    # Сделать запись в бд с uid'ом временем, статусом и типом
    uid = uuid.uuid4().hex
    with db_conn() as db:
        insert = db.prepare(
            "INSERT INTO query (uid, q_type, query, state, dt_start ) VALUES ($1, $2, $3, $4, $5) " +
            "RETURNING id")
        [(queri_id,)] = insert(uid, json['type'], str(json['query']), 'running', datetime.now() )
        # return resp(200, {"theme_id": queri_id})

    # Закинуть в парсер задачу
    if json['type'] == 'friends':
        p = Process(target=get_friends, args=(json['deep'], json['ids'], uid,))
        p.start()
    elif json['type'] == 'audio':
        p = Process(target=get_friends, args=(json['ids'], uid,))
        p.start()

    # Вернуть обратно uid
    return resp(200, {"uid": uid})


#
#
# @app.route('/api/1.0/query/<int:theme_id>', methods=['PUT'])
# def put_theme(theme_id):
#     (json, errors) = theme_validate()
#     if errors:  # list is not empty
#         return resp(400, {"errors": errors})
#
#     with db_conn() as db:
#         update = db.prepare(
#             "UPDATE themes SET title = $2, url = $3 WHERE id = $1")
#         (_, cnt) = update(theme_id, json['title'], json['url'])
#         return resp(affected_num_to_code(cnt), {})
#
#
# @app.route('/api/1.0/query/<int:theme_id>', methods=['DELETE'])
# def delete_theme(theme_id):
#     with db_conn() as db:
#         delete = db.prepare("DELETE FROM themes WHERE id = $1")
#         (_, cnt) = delete(theme_id)
#         return resp(affected_num_to_code(cnt), {})


# ---------------- start -------------------------------------------

if __name__ == '__main__':
    app.debug = True  # enables auto reload during development
    app.run()
