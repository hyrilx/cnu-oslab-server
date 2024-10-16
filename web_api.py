import os
import random
import string
import tarfile
import tempfile
from pathlib import Path

from flask import Flask, request, jsonify, Response
from werkzeug.datastructures import FileStorage

import config
from submit_worker import start_worker, generate_report


def generate_random_id(length=8) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def extract_source(file: FileStorage, random_id: str, user_id: str) -> Path:
    archive_fd, archive_path = tempfile.mkstemp(suffix='.tar')
    os.close(archive_fd)
    file.save(archive_path)

    upload_path = config.SUBMIT_DIR / user_id / random_id
    upload_path.mkdir(exist_ok=True, parents=True)

    with tarfile.open(archive_path, "r") as tar:
        tar.extractall(path=upload_path)
    os.remove(archive_path)

    return upload_path


app = Flask(__name__)


@app.route('/submit', methods=['POST'])
def submit():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    submit_id = generate_random_id()
    user_id = request.form.get('user_id')
    eval_id = int(request.form.get('exp_id'))
    source_path = extract_source(file, submit_id, user_id)

    start_worker(submit_id, source_path, user_id, eval_id)

    return Response(generate_report(submit_id), content_type='text/plain')
