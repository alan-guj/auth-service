# -*- coding: utf-8 -*-
from apps import app,oauth_provider,lm
from flask.ext.login import current_user, login_required
from flask import url_for,request,redirect,render_template
from flask_oauthlib.client import OAuth
from flask.ext.wtf import Form
import logging
import sys

from wtforms import StringField, RadioField, HiddenField, SelectField

from wtforms.validators import DataRequired


@app.route('/register', methods = ['GET','POST'])
@login_required
def register():
    '''用户注册页面'''
    next = request.args.get('next')
    user_id = int(current_user.id)

    class MyRegisterForm(Form):
        mobile = StringField()
        pass
    form = MyRegisterForm()
    if form.validate_on_submit():
        participators = user_api.register(mobile = form.mobile.data,\
                user_id = int(user_id),oauth=oauth_service)
        if participators:
            #return redirect(url_for('register_ok'))
            flash("%s注册成功" % participators[0]['name'])
            if next:
                return redirect(url_for(next))
            return redirect(url_for('my_attend_activities'))
        flash("注册失败，请检查手机号码是否登记过")
    return render_template('register.html',
                        title='注册',
                        form=form)


@app.route('/sso_authorized', methods = ['POST','GET'])
def sso_authorized():
    '''认证通过回调函数'''
    auth_resp = oauth_service.authorized_response()
    if auth_resp is None:
        return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
                )
    log.debug(auth_resp)
    next = request.args.get('next')
    if next is not None:
        return redirect(next)
    return ''

