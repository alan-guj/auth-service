# -*- coding: utf-8 -*-
from apps import app,oauth_provider,lm
from flask.ext.login import current_user, login_required
from flask import url_for,request,redirect,render_template,session,jsonify
from flask import abort
import json
from flask_oauthlib.client import OAuth
from flask.ext.wtf import Form
from .uuid_lib import *
from .user import User
from .auth_server import AuthUser
from flask.ext.login import LoginManager,UserMixin,login_user,current_user
from flask.ext.login import login_required,logout_user
from weixin.client import WeixinMpAPI
from io import BytesIO
import logging
import sys
import qrcode
from resources import *
from wtforms import StringField, RadioField, HiddenField, SelectField
import urllib.request
from wtforms.validators import DataRequired

log = logging.getLogger('sso_web_server_auth')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

@app.route('/sso/login', methods = ['GET','POST'])
@oauth_provider.authorize_handler
def sso_login(*args, **kargs):
    '''用户扫码登录页面'''
    client_id = request.args.get('client_id')
    log.debug('anonymous login:%s',current_user.is_anonymous)
    #判断用户是否已经登录
    if not current_user.is_anonymous:
        #已经登录成功
        session['id']=current_user.id
        return True
    '''生成微信授权的URL的二维码'''
    uuid=create_uuid('')
    log.debug('create_uuid:%s',uuid)
    session['uuid'] = uuid
    return render_template('pc_login.html',
                        title='登录',
                        qrcode_url = url_for('get_auth_qrcode',
                            client_id=request.args.get('client_id'),
                            response_type=request.args.get('response_type'),
                            scope=request.args.get('scope'),
                            redirect_uri=request.args.get('redirect_uri'),
                            uuid = uuid
                            )
                        )


def create_qrcode(accessurl):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=5,
            border=4,
        )

        qr.add_data(accessurl)
        qr.make(fit=True)
        img = qr.make_image()
        return img
    except Exception as e:
        print(e)
        return None

#获取二维码图片
@app.route('/auth_qrcode',methods=['get'])
def get_auth_qrcode():
    '''微信授权的URL'''
    # rep = oauth_service.authorize(
            # callback = url_for(
                # 'sso_authorized', next=request.args.get('next'),
                # uuid=uuid,_external = True
                # )
            # )
    uuid = request.args.get('uuid')
    if uuid is None:
        return 'uuid not found',400

    scope = ("snsapi_userinfo",)
    api = WeixinMpAPI(appid=app.config.get('WEIXIN_CONSUMER_KEY'),
            app_secret=app.config.get('MER_SECRET'),
            redirect_uri=url_for('sso_authorized',
                client_id=request.args.get('client_id'),
                response_type=request.args.get('response_type'),
                scope=request.args.get('scope'),
                redirect_uri=request.args.get('redirect_uri'),
                uuid= uuid,
                _external = True))
    authorize_url = api.get_authorize_url(scope=scope) +'#wechat_redirect'
    log.debug('authorize_url: %s',authorize_url)
    #创建二维码
    set_uuid_true_url(uuid,authorize_url)
    img=create_qrcode(url_for('true_url',uuid=uuid,_external=True))
    out=BytesIO()
    img.save(out, "PNG")

    #返回二维码字节流
    return out.getvalue(),200

@app.route('/sso/true_url')
def true_url():
    uuid = request.args.get('uuid')
    if uuid is not None:
        true_url = get_uuid_true_url(uuid)
        if true_url is not None:
            return redirect(true_url)
    abort(404)

@app.route('/sso/login_delete',methods = ['POST'])
def login_delete():
    log.debug('login_delete')
    if 'uuid' in session:
        uuid = session['uuid']
        log.debug('    uuid:%s',uuid)
        delete_uuid(uuid)
        del session['uuid']
    return 'ok',200


@app.route('/sso/authorize',methods=['GET'])
def sso_authorize():
    '''获取code'''
    uuid = session['uuid']
    log.debug('uuid:%s',uuid)
    rc = get_uuid_auth_result(uuid)
    log.debug('resultinfo:%s', rc)
    if rc is not None:
        if rc['authorized']:
            user = User().query.get(rc['user_id'])
            if user is not None:
                login_user(AuthUser(id = user.id, openid = user.openid,
                mobile = user.mobile, name = user.name,data = user.to_json()))
            # rc['redirect_uri']=url_add_params(rc['redirect_uri'],code=rc['code'])
        return json.dumps(rc),200
    abort(404)

# @app.route('/sso/authorize1',methods=['GET'])
# @oauth_provider.authorize_handler
# def sso_authorize1():
    # '''获取code'''
    # uuid = session['uuid']
    # log.debug('uuid:%s',uuid)
    # rc = get_uuid_auth_result(uuid)
    # log.debug('resultinfo:%s', rc)
    # if rc is not None:
        # if rc['authorized']:
            # user = User().query.get(rc['user_id'])
            # if user is not None:
                # login_user(AuthUser(id = user.id, openid = user.openid,
                # mobile = user.mobile, name = user.name))
                # return True
    # return False


@app.route('/sso/authorized', methods = ['POST','GET'])
def sso_authorized():
    '''微信扫码通过，返回微信OAuth的code'''
    code = request.args.get('code')
    uuid = request.args.get('uuid')
    log.debug('code=%s',code)
    log.debug('uuid=%s',uuid)

    if code == 'authdeny':
        return 'False'

    api = WeixinMpAPI(appid=app.config.get('WEIXIN_CONSUMER_KEY'),
            app_secret=app.config.get('WEIXIN_CONSUMER_SECRET'),
            redirect_uri=url_for('authorize', _external = True))
    auth_info = api.exchange_code_for_access_token(code = code)

    if not 'openid' in auth_info:
        log.info('exchange_code_for_access_token failed( code = %s )', code)
        return 'False'

    log.debug('auth_info:%s',auth_info)
    #获取用户信息
    user = User.get_user_by_openid(openid = auth_info['openid'])
    # if user is None:
        # #增加用户
        # user = User.add_user(openid = auth_info['openid'])
    if user is None or user.type is None or user.type == 'guest':
        log.error('get user failed, openid=%s',auth_info['openid'])
        #TODO:非注册用户无法使用PC WEB系统，应该将用户重定向到注册页面
        return redirect(REGISTER_PAGE+'?next='+urllib.request.quote(url_for('true_url',uuid=uuid,_external=True)))
    log.debug('user:%s',user.id)
    session['id']=user.id
    session['uuid']=uuid
    login_user(AuthUser(id = user.id, openid = user.openid,
                mobile = user.mobile, name = user.name,data = user.to_json()))
    #获取Code
    rep=oauth_provider.confirm_authorization_request()
    log.debug('rep:%s',rep.headers)
    return render_template('wx_login_success.html')

@app.route('/sso/logout', methods = ['GET'])
def sso_logout():
    logout_user()
    next = request.args.get('next')
    if next:
        return redirect(next)
    return '退出成功'
