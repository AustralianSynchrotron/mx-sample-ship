from . import main
from flask import render_template

@main.route("/")
def hello():
    return "Hello World!"
