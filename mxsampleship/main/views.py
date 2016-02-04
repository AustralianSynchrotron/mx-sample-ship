from . import main
from ..utils import arrival_data
from flask import current_app, render_template, url_for, redirect, abort
from flask.ext.login import login_required, current_user
from flask_wtf import Form
from wtforms import (StringField, PasswordField, SubmitField, BooleanField,
                     SelectField)
from wtforms.validators import DataRequired
from portalapi.portalapi import RequestFailed
import requests
from urllib.parse import urljoin


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
    container_type = SelectField(
        'Sample Type',
        choices=[('pucks', 'pucks'), ('cassette', 'cassette'), ('canes', 'canes')]
    )
    container_ids_1 = StringField('ID(s) for adaptor/cassette 1')
    container_ids_2 = StringField('ID(s) for adaptor/cassette 2')
    submit = SubmitField()


@main.route('/')
def index():
    return redirect(url_for('.shipment_form'))


@main.route('/shipment-form', methods=['GET', 'POST'])
@login_required
def shipment_form():

    # There is a bug with the portal api server which causes an invalid
    # response when a user has no EPNs. This causes a RequestFailed exception
    # to be raised.
    try:
        visits = current_user.api.get_scientist_visits()
    except RequestFailed:
        visits = []

    # TODO: if visits is empty redirect to another page?
    epn_text_fmt = '{0.epn} @ {0.start_time:%Y-%m-%d %H:%M}'
    epn_choices = [(visit.epn, epn_text_fmt.format(visit)) for visit in visits]

    class UserShipmentForm(ShipmentForm):
        epn = SelectField('Experiment Proposal Number', choices=epn_choices)

    form = UserShipmentForm()
    if form.validate_on_submit():
        epn = form.data['epn']
        containers = '{container_ids_1} | {container_ids_2}'.format(**form.data)
        dewar = {
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
        url = urljoin(current_app.config['PUCKTRACKER_URL'], 'dewars/new')
        response = requests.post(url, json=dewar)
        # TODO: Handle errors
        shipment_id = response.json()['data']['_id']
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
    endpoint = 'dewars/%s' % shipment_id
    url = urljoin(current_app.config['PUCKTRACKER_URL'], endpoint)
    response = requests.get(url)
    # TODO: Handle errors
    if response.status_code != 200:
        abort(404)
    dewar = response.json()['data']
    dewar['qrcode_data'] = arrival_data(dewar)
    return render_template('main/shipment-slip.html', dewars=[dewar])
