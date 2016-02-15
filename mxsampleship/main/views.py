from . import main
from ..utils import arrival_data
from flask import current_app, request, render_template, url_for, redirect, abort
from flask.ext.login import login_required, current_user
from flask_wtf import Form
from wtforms import (StringField, PasswordField, SubmitField, BooleanField,
                     SelectField, FieldList)
from wtforms.validators import DataRequired
from portalapi.portalapi import RequestFailed
import requests
from six.moves.urllib.parse import urljoin


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
    email = StringField('Contact Email', validators=[DataRequired()])
    # epn field must be generated when subclassing the ShipmentForm
    other_epn = StringField('Other EPN')
    return_dewar = BooleanField('Return dewar?')
    courier = StringField('Courier')
    courier_account = StringField('Courier Account Number')
    container_type = SelectField(
        'Sample Type',
        choices=[('pucks', 'pucks'), ('cassettes', 'cassettes'), ('canes', 'canes')]
    )
    pucks = FieldList(StringField('Puck IDs'), min_entries=8)
    cassettes = FieldList(StringField('Cassette IDs'), min_entries=2)
    canes = StringField('Cane ID')
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

    epn_text_fmt = '{0.epn} @ {0.start_time:%Y-%m-%d %H:%M}'
    epn_choices = [(visit.epn, epn_text_fmt.format(visit)) for visit in visits]
    epn_choices.append(('other', 'other'))

    class UserShipmentForm(ShipmentForm):
        epn = SelectField('Experiment Proposal Number', choices=epn_choices)

    form = UserShipmentForm()
    if form.validate_on_submit():
        epn = form.data['epn']
        if epn == 'other':
            epn = form.data['other_epn']
        container_type = form.data['container_type']
        if container_type in ('pucks', 'cassettes'):
            containers = ','.join(form.data[container_type])
        else:
            containers = form.data['canes']
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
            'containerType': container_type,
            'expectedContainers': containers,
        }
        url = urljoin(current_app.config['PUCKTRACKER_URL'], 'dewars/new')
        response = requests.post(url, json=dewar)
        # TODO: Handle errors
        name = response.json()['data']['name']
        return redirect(url_for('.shipment', dewar_name=name))

    if request.method == 'GET':
        scientist = current_user.api.get_scientist()
        full_name = '{user.first_names} {user.last_name}'.format(user=scientist)
        form.owner.data = full_name
        form.institute.data = scientist.organisation.name_long
        form.email.data = scientist.email
        form.phone.data = scientist.telephone_number_1

    return render_template('main/shipment-form.html', form=form)


@main.route('/shipment/<dewar_name>')
@login_required
def shipment(dewar_name):
    endpoint = 'dewars/%s' % dewar_name
    url = urljoin(current_app.config['PUCKTRACKER_URL'], endpoint)
    response = requests.get(url)
    # TODO: Handle errors
    if response.status_code != 200:
        abort(404)
    dewar = response.json().get('data', {})
    if not dewar:  # TODO: Check submitter
        abort(403)
    dewar['expectedContainers'] = dewar['expectedContainers'].strip(',')
    dewar['qrcode_data'] = arrival_data(dewar)
    return render_template('main/shipment-slip.html', dewars=[dewar])
