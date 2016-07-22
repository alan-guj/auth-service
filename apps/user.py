# coding: utf-8
from sqlalchemy.orm import relationship
from apps import db,oauth_provider,img_api
from flask import request,jsonify,abort
from .ret import *

from apps import app
import logging
import sys
log = logging.getLogger('oauth_user_service')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.INFO)






class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(80), index=True, unique=True)
    name = db.Column(db.String(80), index=True)
    nickname = db.Column(db.String(80))
    mobile = db.Column(db.String(80), index=True)
    email = db.Column(db.String(80), index=True)
    portrait_uri = db.Column(db.String(128))
    desc = db.Column(db.String(2048))
    enterprise_id = db.Column(db.Integer, index=True) #企业的ID
    type = db.Column(db.String(60))  #system, guest, user, enterprise_user




    @staticmethod
    def add_user(openid, mobile=None, name=None,nickname=None):
        u = User(openid=openid, mobile=mobile, name=name,nickname = nickname,type='guest')
        try:
            db.session.add(u)
            db.session.commit()
        except Exception as e:
            print(e)
            return None
        return u

    @staticmethod
    def get_user_by_openid(openid):
        return User.query.filter_by(openid=openid).first()
    @staticmethod
    def get_user(id):
        return User.query.get(id)

    def to_json(self):
        return {
            'id':self.id,
            'name':self.name,
            'nickname':self.nickname,
            'openid':self.openid,
            'mobile':self.mobile,
            'email':self.email,
            'portrait_uri':img_api.get_img(self.portrait_uri),
            'desc':self.desc,
            'type':self.type,
            'enterprise_id':self.enterprise_id
        }

    def fuzzy_json(self):
        '''对用户信息进行模糊化处理'''
        return {
                'id':self.id,
                'name':fuzz_name(self.name),
                'nickname':self.nickname,
                'email':fuzz_email(self.email),
                'mobile':fuzz_mobile(self.mobile),
                'enterprise_id':self.enterprise_id,
                'portrait_uri':img_api.get_img(self.portrait_uri),
                }


    def check_password(self,password):
        return True

@app.route('/api/v1.0/users/current')
@oauth_provider.require_oauth('userinfo')
def userinfo():
    user = request.oauth.user
    return jsonify(user=user.to_json())

@app.route('/api/v1.0/users/current', methods = ['PUT'])
@oauth_provider.require_oauth('userinfo')
def userinfo_update():
    user = request.oauth.user
    if not request.json:
        return ret_no_json
    if 'portrait_uri' in request.json and type(request.json['portrait_uri']) is not str:
        return ret_parm_err('portrait_uri must be string')
    if 'email' in request.json and type(request.json['email']) is not str:
        return ret_parm_err('email must be string')
    if 'desc' in request.json and type(request.json['desc']) is not str:
        return ret_parm_err('desc must be string')
    user.portrait_uri=request.json.get('portrait_uri',user.portrait_uri)
    user.email = request.json.get('email',user.email)
    user.desc = request.json.get('desc',user.desc)
    try:
        db.session.commit()
        return jsonify(user=user.to_json())
    except Exception as e:
        print(e)
        return ret_run_err(e)

@app.route('/api/v1.0/users/<int:user_id>', methods = ['PUT'])
@oauth_provider.require_oauth('userinfo')
def update_user(user_id):
    if not request.json:
        return ret_no_json
    # if 'mobile' in request.json and type(request.json['mobile']) is not str:
        # return ret_parm_err('mobile must be string')
    # if 'name' in request.json and type(request.json['name']) is not str:
        # return ret_parm_err('name must be string')
    # if 'type' in request.json and type(request.json['type']) is not str:
        # return ret_parm_err('name must be string')
    # if 'enterprise_id' in request.json and type(request.json['enterprise_id']) is not int:
        # return ret_parm_err('enterprise_id must int')

    u = User().query.get(user_id)
    if not u:
        return ret_not_found('user')

    try:
        name = request.json.get('name',u.name)
        assert name is None or type(name) is str
        mobile = request.json.get('mobile',u.mobile)
        assert mobile is None or type(mobile) is str
        enterprise_id = request.json.get('enterprise_id',u.enterprise_id)
        assert enterprise_id is None or type(enterprise_id) is int
        user_type = u.type
    except Exception as e:
        return ret_parm_err(e)

    if name is not None and mobile is not None and enterprise_id is not None:
        user_type='enterprise_user'
    elif name is not None and mobile is not None and enterprise_id is None:
        user_type = 'user'
    else:
        return ret_parm_err('mobile is none and enterprise_id is not None')


    u.mobile = mobile
    u.enterprise_id= enterprise_id
    u.type = user_type
    u.name = name

    try:
        db.session.commit()
        return jsonify({'user': u.to_json()})
    except Exception as e:
        print(e)
        return ret_run_err(e)


@app.route('/api/v1.0/users/registration', methods = ['POST'])
@oauth_provider.require_oauth('userinfo')
def user_registration():
    '''用户注册'''
    user = request.oauth.user

    log.debug('access_token:%s',request.oauth.token)

    if user.type is not None and user.type.startswith('system_'):
        #系统用户不允许注册
        return ret_run_err('system user cannot register')

    if not request.json:
        return ret_no_json
    if 'mobile' not in request.json or type(request.json['mobile']) is not str:
        return ret_parm_err('mobile not exist or wrong type')
    if 'enterprise_id' in request.json and type(request.json['enterprise_id']) is not int:
        return ret_parm_err('enterprise_id must be int')

    mobile=request.json.get('mobile')
    enterprise_id = request.json.get('enterprise_id',user.enterprise_id)

    #TODO:已经注册的用户是否允许再次注册？

    if enterprise_id is None:
        #没有企业标识
        user_type = 'user'
    else:
        user_type = 'enterprise_user'

    try:
        user.mobile = mobile
        user.enterprise_id = enterprise_id
        user.type = user_type
        db.session.commit()
        return jsonify(user=user.to_json())
    except Exception as e:
        print(e)
        return ret_run_err(e)

@app.route('/api/v1.0/users', methods=['GET'])
@app.route('/api/v1.0/users/<int:id>')
@oauth_provider.require_oauth('userinfo')
def get_users(id = None):
    if not id:
        id = request.args.get('id')
    mobile = request.args.get('mobile')
    openid = request.args.get('openid')
    name = request.args.get('name')
    tt=[]
    query=db.session.query(User)
    if id:
        query=query.filter(User.id == id)
    if mobile:
        query=query.filter(User.mobile ==mobile)
    if openid:
        query = query.filter(User.openid == openid)
    if name:
        query = query.filter(User.name == name)

    print(query)
    ts=query.all()

    #取当前用户信息
    cur_user = request.oauth.user
    if not ts:
        abort(404)
    for t in ts:
        if cur_user.type.startswith('system_') or cur_user.id == t.id:
            #查询到的用户不是当前用户
            tt.append(t.to_json())
        else:
            tt.append(t.fuzzy_json())
    print(tt)
    return jsonify({'users':tt})


def fuzz_name(name):
    return name
    if name is None:
        return None
    return '*'+name[1:]

def fuzz_mobile(mobile):
    if mobile is None:
        return None
    return mobile[:3]+'*****'+mobile[len(mobile)-3:]

def fuzz_email(email):
    if email is None:
        return None
    sp_email = email.split('@')
    if len(sp_email) != 2:
        return '*'
    user = sp_email[0]
    domain = sp_email[1]
    return user[:1]+'***'+user[len(user)-1:]+'@'\
            +domain[:2]+'***'+domain[len(domain)-3:]
