# -*- coding: utf-8 -*-
from apps import app,oauth_provider,lm
from flask import g, render_template, request, jsonify, make_response, url_for
from flask import redirect,session
from flask.ext.login import LoginManager,UserMixin,login_user,current_user
from flask.ext.login import login_required
from weixin.client import WeixinMpAPI,WeixinAPI
from datetime import datetime,timedelta
from .user import User
import logging
import sys
log = logging.getLogger('flask_oauthlib')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)


class AuthUser(UserMixin):
    id = None
    openid = None
    name = None
    mobile = None
    cur_activity = None
    data = None
    def __init__(self,id,openid, mobile, name,data):
        self.id = id
        self.openid = openid
        self.name = name
        self.mobile = mobile
        self.data = data

@lm.user_loader
def load_user(id):
    log.debug('load_user:%s',id)
    user = User().query.get(int(id))
    if not user:
        return None
    return AuthUser(id = id, openid = user.openid,
            name = user.name, mobile = user.mobile,data=user.to_json())


@lm.unauthorized_handler
def unauthorized():
    '''没有登录过，通过微信登录'''
    scope = ("snsapi_userinfo",)
    api = WeixinMpAPI(appid=app.config.get('WEIXIN_CONSUMER_KEY'),
            app_secret=app.config.get('WEIXIN_CONSUMER_SECRET'),
            redirect_uri=url_for('authorized',
                client_id=request.args.get('client_id'),
                response_type=request.args.get('response_type'),
                scope=request.args.get('scope'),
                redirect_uri=request.args.get('redirect_uri'),
                _external = True))
    authorize_url = api.get_authorize_url(scope=scope) +'#wechat_redirect'
    log.debug('authorize_url: %s',authorize_url)
    return redirect(authorize_url)



@app.route('/oauth/authorize', methods = ['GET'])
@login_required
@oauth_provider.authorize_handler
def authorize(*args, **kargs):
    '''已经登录成功，直接返回'''
    return True

@app.route('/oauth/authorized', methods = ['GET', 'POST'])
@oauth_provider.authorize_handler
def authorized(*args, **kargs):
    '''微信的OAuth Redirect Endpoint'''
    code = request.args.get('code')

    log.debug('code=%s',code)
    if code == 'authdeny':
        return False

    api = WeixinMpAPI(appid=app.config.get('WEIXIN_CONSUMER_KEY'),
            app_secret=app.config.get('WEIXIN_CONSUMER_SECRET'),
            redirect_uri=url_for('authorize', _external = True))
    auth_info = api.exchange_code_for_access_token(code = code)

    if not 'openid' in auth_info:
        log.info('exchange_code_for_access_token failed( code = %s )', code)
        return False

    log.debug('auth_info:%s',auth_info)
    #获取用户的微信信息
    api = WeixinMpAPI(access_token=auth_info['access_token'])
    wx_userinfo = api.user(openid = auth_info['openid'])
    log.debug('wx_userinfo: %s',wx_userinfo)
    nickname = wx_userinfo.get('nickname')
    #获取用户信息
    user = User.get_user_by_openid(openid = auth_info['openid'])
    if user is None:
        #增加用户
        user = User.add_user(openid = auth_info['openid'],nickname = nickname)
    if user is None:
        log.error('get user failed, openid=%s',auth_info['openid'])
        return False
    log.debug('user:%s',user)
    session['id'] = user.id
    login_user(AuthUser(id = user.id, openid = user.openid,
        mobile = user.mobile, name = user.name,data = user.to_json()),
        remember = True)
    return True

@app.route('/oauth/access_token', methods = ['GET', 'POST'])
@oauth_provider.token_handler
def access_token():
    return {}

@app.route('/oauth/revoke', methods = ['POST'])
@oauth_provider.revoke_handler
def revoke_token():
    pass


