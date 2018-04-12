import os
import sqlite3
import logging
from pathlib import Path
from flask import Flask, Markup, render_template, request
from heybrochecklog.score import score_log, score_log_from_contents
from heybrochecklog.translate import translate_log, translate_log_from_contents

app = Flask(__name__)
app.config.from_object('config')
app.logger.setLevel(logging.ERROR)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/handle', methods=['POST'])
def handle():
    action = request.form.get('action')
    text = request.form.get('log-content', '')
    file_ = request.files.get('logfile', None)
    if text:
        return handle_text(action, text)
    elif file_:
        return handle_file(action, file_)
    else:
        return render_template('index.html')


def handle_file(action, file_):
    filename = get_filename()
    file_.save(filename)
    log_file = Path(filename)
    if action == 'Score':
        contents = score_log(log_file, markup=True)
        contents['contents'] = Markup(contents['contents'])
        return render_template('score.html', contents=contents)
    elif action == 'Translate':
        contents = translate_log(log_file)
        if 'log' in contents:
            contents['log'] = Markup(contents['log'])
        return render_template('translate.html', contents=contents)


def handle_text(action, text):
    with open(get_filename(), 'w') as log_file:
        log_file.write(text)
    if action == 'Score':
        contents = score_log_from_contents(text)
        contents['contents'] = Markup(contents['contents'])
        return render_template('score.html', contents=contents)
    elif action == 'Translate':
        contents = translate_log_from_contents(text)
        if 'log' in contents:
            contents['log'] = Markup(contents['log'])
        return render_template('translate.html', contents=contents)


def get_filename():
    directory = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(directory, 'logs.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(ID) FROM LogFiles')
    previousid = cursor.fetchone()[0]
    logid = previousid + 1 if previousid else 1

    cursor.execute('INSERT INTO LogFiles (ID) VALUES (?)', (logid,))
    conn.commit()
    conn.close()

    return os.path.join(
        app.config['UPLOAD_FOLDER'], '{:04d}.log'.format(logid))
