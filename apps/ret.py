from flask import jsonify


def ret(message,code):
    print('error message %s, error code %d' % (message, code))
    return jsonify({'message': message}),code
def ret_no_json():
    return ret('请求中缺少JSON内容',400)
def ret_parm_err(para):
    return ret('参数错误：%s' % para, 400)
def ret_run_err(message):
    return ret('运行时错误：%s' % message, 400)
def ret_not_found(obj):
    return ret('对象(%s)不存在' % obj, 404)


