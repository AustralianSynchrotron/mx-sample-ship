Website for submitting MX sample shipping information.

## Installation

```
sudo yum install libjpeg-turbo-devel zlib-devel
pip install --extra-index https://aspypi.synchrotron.org.au .
```

## Running

```bash
export SECRET_KEY='something secret'
export SAMPLE_SHIP_CONFIG='development' # or 'production'
./manage.py runserver
```

## Testing

```bash
pip install -r requirements.txt --extra-index https://aspypi.synchrotron.org.au
pip install --extra-index https://aspypi.synchrotron.org.au -e .
SECRET_KEY=whatever py.test
```
