from . import auth
from ..models import User
from portalapi.authentication import AuthenticationFailed
from flask import request, session, render_template, redirect, url_for, flash
from flask_wtf import Form
from flask.ext.login import login_required, login_user, logout_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import json


class LoginForm(Form):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    status = 200
    if form.validate_on_submit():
        # TODO: Authenticate
        try:
            user = User(form.data['username'], form.data['password'])
        except AuthenticationFailed:
            status = 401
            flash('Email or password incorrect', 'danger')
        else:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
    return render_template('auth/login.html', form=form), status


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))
