#!flask/bin/python
from flask import Flask
from flask_oauthlib.provider import OAuth2Provider
from flask_oauthlib.client import OAuth
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager,UserMixin,login_user,current_user
import os
from flask.ext.session import Session
from flask.ext.cors import CORS
os.environ['OAUTHLIB_INSECURE_TRANSPORT']='1'
app = Flask(__name__)
oauth_provider = OAuth2Provider(app)
db = SQLAlchemy(app)
CORS(app)
app.config.from_object('config')
'''初始化LoginManager'''
lm = LoginManager()
lm.init_app(app)
# lm.login_view = 'login'
# lm.session_protection = 'strong'

oauth = OAuth(app)
oauth_service = oauth.remote_app('user_service',app_key = 'USER_SERVICE')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
from sdk.img_api import ImgApi
img_api = ImgApi(oauth_service)

from apps import app,auth_server,auth_provider
from apps import sso_server
from apps import user,entity

# Session(app)
db.create_all()
