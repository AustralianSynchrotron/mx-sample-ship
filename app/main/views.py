from . import main
from .. import mongo
from ..utils import arrival_url
from flask import render_template, url_for, redirect, abort
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ShipmentForm(Form):
    owner = StringField('Full Name', validators=[DataRequired()])
    epn = StringField('EPN', validators=[DataRequired()])
    submit = SubmitField()


@main.route('/', methods=['GET', 'POST'])
def index():
    form = ShipmentForm()
    if form.validate_on_submit():
        epn = form.data['epn']
        shipment_id = mongo.db.dewars.find().count() + 1
        epn_dewar_num = mongo.db.dewars.find({'epn': epn}).count() + 1
        dewar_name = 'd-{epn}-{n}'.format(epn=epn, n=epn_dewar_num)
        dewar = {
            'shipment_id': shipment_id,
            'name': dewar_name,
            'owner': form.data['owner'],
            'epn': epn,
        }
        mongo.db.dewars.insert(dewar)
        return redirect(url_for('.shipment', shipment_id=shipment_id))
    return render_template('index.html', form=form)


@main.route('/shipment/<int:shipment_id>')
def shipment(shipment_id):
    dewars = list(mongo.db.dewars.find({'shipment_id': shipment_id}))
    for dewar in dewars:
        dewar['qrcode_data'] = arrival_url(dewar)
    if not dewars:
        abort(404)
    return render_template('shipment.html', dewars=dewars)
