Website for submitting MX sample shipping information.

## Running

```bash
export SECRET_KEY='something secret'
export SAMPLE_SHIP_CONFIG='development' # or 'production'
./manage.py runserver
```

## Testing

```bash
pip install -e .
py.test
```
