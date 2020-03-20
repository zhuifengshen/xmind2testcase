#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import logging
import os
import re
import arrow
import sqlite3
from contextlib import closing
from os.path import join, exists
from werkzeug.utils import secure_filename
from xmind2testcase.zentao import xmind_to_zentao_csv_file
from xmind2testcase.testlink import xmind_to_testlink_xml_file
from xmind2testcase.utils import get_xmind_testsuites, get_xmind_testcase_list
from flask import Flask, request, send_from_directory, g, render_template, abort, redirect, url_for

here = os.path.abspath(os.path.dirname(__file__))
log_file = os.path.join(here, 'running.log')
# log handler
formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s  [%(module)s - %(funcName)s]: %(message)s')
file_handler = logging.FileHandler(log_file, encoding='UTF-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
# xmind to testcase logger
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)
root_logger.setLevel(logging.DEBUG)
# flask and werkzeug logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addHandler(file_handler)
werkzeug_logger.addHandler(stream_handler)
werkzeug_logger.setLevel(logging.DEBUG)

# global variable
UPLOAD_FOLDER = os.path.join(here, 'uploads')
ALLOWED_EXTENSIONS = ['xmind']
DEBUG = True
DATABASE = os.path.join(here, 'data.db3')
HOST = '0.0.0.0'

# flask app
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.urandom(32)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def init():
    app.logger.info('Start initializing the database...')
    if not exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    if not exists(DATABASE):
        init_db()
    app.logger.info('Congratulations! the xmind2testcase webtool database has initialized successfully!')


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def insert_record(xmind_name, note=''):
    c = g.db.cursor()
    now = str(arrow.now())
    sql = "INSERT INTO records (name,create_on,note) VALUES (?,?,?)"
    c.execute(sql, (xmind_name, now, str(note)))
    g.db.commit()


def delete_record(filename, record_id):
    xmind_file = join(app.config['UPLOAD_FOLDER'], filename)
    testlink_file = join(app.config['UPLOAD_FOLDER'], filename[:-5] + 'xml')
    zentao_file = join(app.config['UPLOAD_FOLDER'], filename[:-5] + 'csv')

    for f in [xmind_file, testlink_file, zentao_file]:
        if exists(f):
            os.remove(f)

    c = g.db.cursor()
    sql = 'UPDATE records SET is_deleted=1 WHERE id = ?'
    c.execute(sql, (record_id,))
    g.db.commit()


def delete_records(keep=20):
    """Clean up files on server and mark the record as deleted"""
    sql = "SELECT * from records where is_deleted<>1 ORDER BY id desc LIMIT -1 offset {}".format(keep)
    assert isinstance(g.db, sqlite3.Connection)
    c = g.db.cursor()
    c.execute(sql)
    rows = c.fetchall()
    for row in rows:
        name = row[1]
        xmind_file = join(app.config['UPLOAD_FOLDER'], name)
        testlink_file = join(app.config['UPLOAD_FOLDER'], name[:-5] + 'xml')
        zentao_file = join(app.config['UPLOAD_FOLDER'], name[:-5] + 'csv')

        for f in [xmind_file, testlink_file, zentao_file]:
            if exists(f):
                os.remove(f)

        sql = 'UPDATE records SET is_deleted=1 WHERE id = ?'
        c.execute(sql, (row[0],))
        g.db.commit()


def get_latest_record():
    found = list(get_records(1))
    if found:
        return found[0]


def get_records(limit=8):
    short_name_length = 120
    c = g.db.cursor()
    sql = "select * from records where is_deleted<>1 order by id desc limit {}".format(int(limit))
    c.execute(sql)
    rows = c.fetchall()

    for row in rows:
        name, short_name, create_on, note, record_id = row[1], row[1], row[2], row[3], row[0]

        # shorten the name for display
        if len(name) > short_name_length:
            short_name = name[:short_name_length] + '...'

        # more readable time format
        create_on = arrow.get(create_on).humanize()
        yield short_name, name, create_on, note, record_id


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def check_file_name(name):
    secured = secure_filename(name)
    if not secured:
        secured = re.sub('[^\w\d]+', '_', name)  # only keep letters and digits from file name
        assert secured, 'Unable to parse file name: {}!'.format(name)
    return secured + '.xmind'


def save_file(file):
    if file and allowed_file(file.filename):
        # filename = check_file_name(file.filename[:-6])
        filename = file.filename
        upload_to = join(app.config['UPLOAD_FOLDER'], filename)

        if exists(upload_to):
            filename = '{}_{}.xmind'.format(filename[:-6], arrow.now().strftime('%Y%m%d_%H%M%S'))
            upload_to = join(app.config['UPLOAD_FOLDER'], filename)

        file.save(upload_to)
        insert_record(filename)
        g.is_success = True
        return filename

    elif file.filename == '':
        g.is_success = False
        g.error = "Please select a file!"

    else:
        g.is_success = False
        g.invalid_files.append(file.filename)


def verify_uploaded_files(files):
    # download the xml directly if only 1 file uploaded
    if len(files) == 1 and getattr(g, 'is_success', False):
        g.download_xml = get_latest_record()[1]

    if g.invalid_files:
        g.error = "Invalid file: {}".format(','.join(g.invalid_files))


@app.route('/', methods=['GET', 'POST'])
def index(download_xml=None):
    g.invalid_files = []
    g.error = None
    g.download_xml = download_xml
    g.filename = None

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        g.filename = save_file(file)
        verify_uploaded_files([file])
        delete_records()

    else:
        g.upload_form = True

    if g.filename:
        return redirect(url_for('preview_file', filename=g.filename))
    else:
        return render_template('index.html', records=list(get_records()))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/<filename>/to/testlink')
def download_testlink_file(filename):
    full_path = join(app.config['UPLOAD_FOLDER'], filename)

    if not exists(full_path):
        abort(404)

    testlink_xmls_file = xmind_to_testlink_xml_file(full_path)
    filename = os.path.basename(testlink_xmls_file) if testlink_xmls_file else abort(404)

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/<filename>/to/zentao')
def download_zentao_file(filename):
    full_path = join(app.config['UPLOAD_FOLDER'], filename)

    if not exists(full_path):
        abort(404)

    zentao_csv_file = xmind_to_zentao_csv_file(full_path)
    filename = os.path.basename(zentao_csv_file) if zentao_csv_file else abort(404)

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/preview/<filename>')
def preview_file(filename):
    full_path = join(app.config['UPLOAD_FOLDER'], filename)

    if not exists(full_path):
        abort(404)

    testsuites = get_xmind_testsuites(full_path)
    suite_count = 0
    for suite in testsuites:
        suite_count += len(suite.sub_suites)

    testcases = get_xmind_testcase_list(full_path)

    return render_template('preview.html', name=filename, suite=testcases, suite_count=suite_count)


@app.route('/delete/<filename>/<int:record_id>')
def delete_file(filename, record_id):

    full_path = join(app.config['UPLOAD_FOLDER'], filename)
    if not exists(full_path):
        abort(404)
    else:
        delete_record(filename, record_id)
    return redirect('/')


@app.errorhandler(Exception)
def app_error(e):
    return str(e)


def launch(host=HOST, debug=True, port=5001):
    init()  # initializing the database
    app.run(host=host, debug=debug, port=port)


if __name__ == '__main__':
    init()  # initializing the database
    app.run(HOST, debug=DEBUG, port=5001)
