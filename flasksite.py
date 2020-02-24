import os
import json
import sys
from flask import Flask, request
from werkzeug.utils import secure_filename
from flask import send_from_directory

# default parameters, can be overwritten by command line arguments
PORT = 8000
UPLOAD_FOLDER = './PEBRAcloud_files'

# fixed parameters
ALLOWED_EXTENSIONS = {'txt', 'db', 'xlsx'}
ALLOWED_FOLDERS = {'data', 'backups', 'passwords'}
# TODO: generate secure key, http://flask.pocoo.org/docs/quickstart/#sessions
SECRET_KEY = 'SECRET'
# TODO: generate secure auth token
AUTH_TOKEN = 'TOKEN'


dev_mode = "dev" in sys.argv
for arg in sys.argv:
    if arg.startswith('port='):
        PORT=int(arg[5:])
    if arg.startswith('files='):
        UPLOAD_FOLDER=arg[6:]
print("running in development mode" if dev_mode else "running in production mode")
print("running on port '%s'" % PORT)
print("storing files in '%s'" % UPLOAD_FOLDER)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY
app.config['AUTH_TOKEN'] = AUTH_TOKEN


# create all folders
for folder in ALLOWED_FOLDERS:
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], folder), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'archive', '%s-archive' % folder), exist_ok=True)


def check_token(request):
    if 'token' not in request.headers:
        return False
    request_token = request.headers['token']
    return app.config['AUTH_TOKEN'] == request_token


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def allowed_file(filename):
    return '.' in filename and get_file_extension(filename) in ALLOWED_EXTENSIONS


def allowed_folder(foldername):
    return foldername.lower() in ALLOWED_FOLDERS


@app.route('/upload/<folder>', methods=['POST'])
def upload_file(folder):
    """
    Uploads a file to the given folder. If a file with the same file name exists, it moves the existing one to the
    archive folder.
    """
    if not check_token(request):
        print('Auth error')
        return 'Auth error', 401
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
    """
    Downloads the file with matching username from the given folder.
    """
    if not check_token(request):
        print('Auth error')
        return 'Auth error', 401
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
    """
    Checks if a file for the given username exists in the given folder.
    """
    if not check_token(request):
        print('Auth error')
        return 'Auth error', 401
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
    return "<h1>PEBRAcloud</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=dev_mode, use_reloader=dev_mode)

