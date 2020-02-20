import os
from flask import Flask, request
from werkzeug.utils import secure_filename
from flask import send_from_directory


UPLOAD_FOLDER = './FILES'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_FOLDERS = {'data', 'backups', 'passwords'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# TODO: generate secure key, http://flask.pocoo.org/docs/quickstart/#sessions
app.config['SECRET_KEY'] = 'SECRET'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_folder(foldername):
    return foldername.lower() in ALLOWED_FOLDERS


@app.route('/', methods=['POST'])
def upload_file():
    if 'folder' not in request.values:
        print('Missing folder')
        return 'Missing folder', 400
    folder = request.values['folder']
    if not allowed_folder(folder):
        print('Bad folder')
        return 'Bad folder', 400
    # check if the post request has the file part
    if 'file' not in request.files:
        print('No file part')
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        print('Missing filename')
        return 'Missing filename', 400
    if not allowed_file(file.filename):
        print('Bad filename')
        return 'Bad filename', 400
    if file:
        filename = secure_filename(file.filename)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], folder), exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], folder, filename))
        return 'Upload successful', 201


@app.route('/', methods=['GET'])
def root():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="data" method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/files/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

