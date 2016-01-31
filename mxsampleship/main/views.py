from . import main
from .. import mongo
from ..utils import arrival_url
from flask import render_template, url_for, redirect, abort
from flask.ext.login import login_required, current_user
from flask_wtf import Form
from wtforms import (StringField, PasswordField, SubmitField, BooleanField,
                     SelectField)
from wtforms.validators import DataRequired
import uuid


class ShipmentForm(Form):
    owner = StringField('Full Name', validators=[DataRequired()])
    department = StringField('Department')
    institute = StringField('Institute')
    street_address = StringField('Street Address')
    city = StringField('City')
    state = StringField('State')
    postcode = StringField('Post Code')
    country = StringField('Country')
    phone = StringField('Contact Phone Number')
    email = StringField('Contact Email')
    # epn field must be generated when subclassing the ShipmentForm
    return_dewar = BooleanField('Return dewar?')
    courier = StringField('Courier')
    courier_account = StringField('Courier Account Number')
    container_type = SelectField('Sample Type',
                                 choices=[('cassette', 'cassette'),
                                          ('pucks', 'pucks'),
                                          ('canes', 'canes'),
                                         ])
    container_ids_1 = StringField('ID(s) for adaptor/cassette 1')
    container_ids_2 = StringField('ID(s) for adaptor/cassette 2')
    submit = SubmitField()


@main.route('/')
def index():
    return redirect(url_for('.shipment_form'))


@main.route('/shipment-form', methods=['GET', 'POST'])
@login_required
def shipment_form():

    visits = current_user.api.get_scientist_visits()
    epn_choices = [(visit.epn, visit.epn) for visit in visits]
    class UserShipmentForm(ShipmentForm):
        epn = SelectField('EPN', choices=epn_choices)

    form = UserShipmentForm()
    if form.validate_on_submit():
        epn = form.data['epn']
        shipment_id = str(uuid.uuid4())
        epn_dewar_num = mongo.db.dewars.find({'epn': epn}).count() + 1
        dewar_name = 'd-{epn}-{n}'.format(epn=epn, n=epn_dewar_num)
        containers = '{container_ids_1} | {container_ids_2}'.format(**form.data)
        dewar = {
            'shipment_id': shipment_id,
            'name': dewar_name,
            'epn': epn,
            'owner': form.data['owner'],
            'department': form.data['department'],
            'institute': form.data['institute'],
            'streetAddress': form.data['street_address'],
            'city': form.data['city'],
            'state': form.data['state'],
            'postcode': form.data['postcode'],
            'country': form.data['country'],
            'phone': form.data['phone'],
            'email': form.data['email'],
            'returnDewar': form.data['return_dewar'],
            'courier': form.data['courier'],
            'courierAccount': form.data['courier_account'],
            'containerType': form.data['container_type'],
            'expectedContainers': containers,
        }
        mongo.db.dewars.insert(dewar)
        return redirect(url_for('.shipment', shipment_id=shipment_id))
    scientist = current_user.api.get_scientist()
    full_name = '{user.first_names} {user.last_name}'.format(user=scientist)
    form.owner.data = full_name
    form.institute.data = scientist.organisation.name_long
    form.email.data = scientist.email
    form.phone.data = scientist.telephone_number_1
    return render_template('main/shipment-form.html', form=form)


@main.route('/shipment/<shipment_id>')
@login_required
def shipment(shipment_id):
    dewars = list(mongo.db.dewars.find({'shipment_id': shipment_id}))
    for dewar in dewars:
        dewar['qrcode_data'] = arrival_url(dewar)
    if not dewars:
        abort(404)
    return render_template('main/shipment-slip.html', dewars=dewars)
