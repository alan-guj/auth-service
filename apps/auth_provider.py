# coding: utf-8
from apps import app,oauth_provider,db
from .entity import Client,Token, Grant
from .user import User
from flask import g, render_template, request, jsonify, make_response
from flask import session
from datetime import datetime,timedelta
from .uuid_lib import *
import urllib.parse as urlparse
import urllib
from flask.ext.login import current_user, login_required
def get_current_user():
    # if 'id' in session:
        # uid = session['id']
    if current_user.id is not None:
        uid = int(current_user.id)
        return User.query.get(uid)
    return None

@oauth_provider.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth_provider.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()

def url_add_params(url, **params):
    """ 在网址中加入新参数 """
    pr = urlparse.urlparse(url)
    query = dict(urlparse.parse_qsl(pr.query))
    query.update(params)
    prlist = list(pr)
    prlist[4] = urlparse.urlencode(query)
    return urlparse.urlunparse(prlist)


@oauth_provider.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself:ls
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=get_current_user(),
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()


    #如果有UUID，更新对应的UUID
    if 'uuid' in session:
        uuid = session['uuid']
        print(uuid)
        redirect_uri = url_add_params(request.redirect_uri,code=code['code'])
        print(redirect_uri)
        set_uuid_pass_auth(uuid,code['code'],redirect_uri,session['id'])

    return grant


@oauth_provider.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth_provider.tokensetter
def save_token(token, request, *args, **kwargs):
    if request.user is not None:
        user_id = request.user.id
    else:
        user_id = None
    toks = Token.query.filter_by(
        client_id=request.client.client_id,
        user_id= user_id
    )
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token.get('refresh_token',None),
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=user_id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok


@oauth_provider.usergetter
def get_user(username,password,*args,**kwargs):
    user = User.query.filter_by(mobile = username).first()
    if user.check_password(password):
        return user
    return None
