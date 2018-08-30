FROM python:3
WORKDIR /srv/app

COPY requirements.txt /tmp

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .

ENTRYPOINT [ "python", "manage.py" ]
CMD [ "runserver", "-h", "0.0.0.0", "-d" ]
EXPOSE 5000
