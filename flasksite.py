import os
import json
from flask import Flask, request
from werkzeug.utils import secure_filename
from flask import send_from_directory


UPLOAD_FOLDER = './FILES'
ALLOWED_EXTENSIONS = {'txt', 'db', 'xlsx', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# ALLOWED_EXTENSIONS = {'txt', 'db', 'xlsx'}
ALLOWED_FOLDERS = {'data', 'backups', 'passwords'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# TODO: generate secure key, http://flask.pocoo.org/docs/quickstart/#sessions
app.config['SECRET_KEY'] = 'SECRET'


# create all folders
for folder in ALLOWED_FOLDERS:
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], folder), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'archive', '%s-archive' % folder), exist_ok=True)


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def allowed_file(filename):
    return '.' in filename and get_file_extension(filename) in ALLOWED_EXTENSIONS


def allowed_folder(foldername):
    return foldername.lower() in ALLOWED_FOLDERS


@app.route('/upload/<folder>', methods=['POST'])
def upload_file(folder):
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
        target_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
        # if file already exists, move the exisiting file to the archive folder and add a running number '_X'
        if os.path.isfile(target_path):
            file_ext = get_file_extension(filename)
            filename_no_ext = filename[:-(len(file_ext)+1)]
            file_version = 1
            archive_path = os.path.join(app.config['UPLOAD_FOLDER'], 'archive', '%s-archive' % folder, '%s_%s.%s' % (filename_no_ext, file_version, file_ext))
            while os.path.isfile(archive_path):
                file_version += 1
                archive_path = os.path.join(app.config['UPLOAD_FOLDER'], 'archive', '%s-archive' % folder, '%s_%s.%s' % (filename_no_ext, file_version, file_ext))
            os.rename(target_path, archive_path)
        file.save(target_path)
        return 'Upload successful', 201


@app.route('/download/<folder>/<username>', methods=['GET'])
def download(folder, username):
    if not allowed_folder(folder):
        print('Bad folder')
        return 'Bad folder', 400
    path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    filename = None
    for file in os.listdir(path):
        if file.startswith(username):
            filename = file
            break
    if not filename:
        print('Unknown user')
        return 'Unknown user', 400
    return send_from_directory(path, filename)


@app.route('/exists/<folder>/<username>', methods=['GET'])
def exists(folder, username):
    if not allowed_folder(folder):
        print('Bad folder')
        return 'Bad folder', 400
    path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    filename = None
    for file in os.listdir(path):
        if file.startswith(username):
            filename = file
            break
    if not filename:
        return json.dumps({'exists': False})
    return json.dumps({'exists': True})


@app.route('/', methods=['GET'])
def root():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="upload" method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

