
#数据库连接属性

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://oauth_services:oauth_services@localhost/oauth_services_dev'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'development'

#健智聚合服务号
WEIXIN_CONSUMER_KEY = 'wx6f24693b2ec037b3'
WEIXIN_CONSUMER_SECRET = '0e063bbcabcbe2d618bf3a4913091cbf'



# SERVER_NAME = 'auth.ngrok.natapp.cn'
SERVER_NAME = 'dev.jyx365.top'
USER_SERVICE = {
        'consumer_key':'user_service',
        'consumer_secret':'123456',
        'base_url':'http://dev.jyx365.top',
        'access_token_url':'/oauth/access_token',
        'authorize_url':'/oauth/authorize',
        'request_token_params':{'scope': 'userinfo'},
        'access_token_method':'GET'
    }

#顾杰的测试服务号
# WEIXIN_CONSUMER_KEY = 'wx2815bf2baac5a32f'
# WEIXIN_CONSUMER_SECRET = 'f01e90ab273725b8f0b50228c80b04dd'
