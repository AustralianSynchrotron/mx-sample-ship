from . import main
from .. import mongo
from flask import render_template, url_for, redirect
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ShipmentForm(Form):
    name = StringField('Full Name', validators=[DataRequired()])
    submit = SubmitField()



@main.route('/', methods=['GET', 'POST'])
def index():
    form = ShipmentForm()
    if form.validate_on_submit():
        dewar = {
            'owner': form.data['name'],
        }
        mongo.db.dewars.insert(dewar)
        return redirect(url_for('.index'))
    return render_template('index.html', form=form)
