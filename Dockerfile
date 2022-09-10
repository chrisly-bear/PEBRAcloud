FROM python:3.8.2

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# add pip install directory to path so we can run gunicorn
ENV PATH "$PATH:/home/appuser/.local/bin"

# create user for running the app
WORKDIR /home/appuser/code
RUN useradd appuser && chown -R appuser /home/appuser
USER appuser

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "./run.sh" ]
