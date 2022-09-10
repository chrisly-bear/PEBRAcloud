# PEBRAcloud

Custom backup server for [PEBRApp](https://github.com/chrisly-bear/PEBRApp).

## Install Dependencies

```bash
# create virtual environment
python3 -m venv env
# activate virtual environment
source env/bin/activate
# install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

Run `deactivate` if you want to exit the virtual environment.

## Run the Application

By default, the uploaded files will be stored in the working directory, from which python is called (i.e., not necessarily in the project directory). You can pass the `files` parameter to define a specific directory for storing the files. Just make sure that the executing user has read/write access to that location. Don't use `~` to refer to your home directoy as it won't be defined within the Python environment.

Command line parameters:

- `dev` for development mode
- `port=XXXX` for running on port XXXX
- `files=/path/to/folder` folder in which upload files will be stored

Examples:

```bash
# run in production mode on port 8000 with files being stored under ./PEBRAcloud_files
python flasksite.py

# run on port 7777
python flasksite.py port=7777

# run in development mode with debugging and auto-reload enabled
python flasksite.py dev

# store files under /tmp/FILES
python flasksite.py files=/tmp/FILES
```

**IMPORTANT:**
When deploying the app, use the `run.sh` script to start the app. Running via python is not recommended for production use.

### Run in Docker

```bash
# with `docker`
docker build -t pebracloud .
docker run --rm -v $(pwd)/PEBRAcloud_files:/PEBRAcloud_files -p 8000:8000 pebracloud files=/PEBRAcloud_files

# or with `docker-compose`
docker-compose up -d
```
