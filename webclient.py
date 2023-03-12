from flask import Flask, jsonify, request
from service.objects import *
import service.auth_service as auth_service
import service.tactic_service as tactic_service
import database.db_template as db
from flask_cors import CORS
from gevent import pywsgi
from database import model


app = Flask(__name__)
CORS(app, supports_credentials=True)
NOT_CHECK_URL = ['/', '/login', '/tactics', '/order/analysis']
def start(debug=False):
    app.run(host='0.0.0.0', port=8080, debug=debug)

def production():
    server = pywsgi.WSGIServer(('0.0.0.0', 8080), app)
    server.serve_forever()


@app.before_request
def login_required():
    if request.path not in NOT_CHECK_URL:
        try:
            token = request.headers["token"]
            df = auth_service.validate_token(token)
            if len(df) == 0:
                return jsonify(ApiResp(-401, message="您的登录已无效, 请重新登录").to_dict())
        except:
            return jsonify(ApiResp(-401, message="您的登录已无效, 请重新登录").to_dict())


@app.route('/')
def index():
    dict = {'name': 'QUANT SERVER v0.1'}
    return jsonify(dict)


# 登录
@app.post('/login')
def login():
    data = request.json
    token_df = auth_service.authorize(data['name'], data['password'])
    if token_df is not None:
        return jsonify(ApiResp(data={'token': token_df['token'], 'name': token_df['name']}).to_dict())
    else:
        return jsonify(ApiResp(-1).to_dict())


# 信号列表
@app.post('/orders')
def orders():
    data = request.json
    tactic = data.get('tactic')
    state = data.get('state')
    df = tactic_service.get_orders(tactic, state)
    return jsonify(ApiResp(data=json_utils.dataframe2dict(df)).to_dict())


@app.post('/orders/fail')
def fail_orders():
    data = request.json
    id = data.get('id')
    remark = data.get('remark')
    tactic_service.update_order_state(id, remark, model.ORDER_STATE_FAIL)
    return jsonify(ApiResp().to_dict())


@app.post('/orders/pass')
def pass_order():
    data = request.json
    id = data.get('id')
    remark = data.get('remark')
    tactic_service.update_order_state(id, remark, model.ORDER_STATE_PASS)
    return jsonify(ApiResp().to_dict())

@app.post('/orders/cancel')
def cancel_order():
    data = request.json
    id = data.get('id')
    remark = data.get('remark')
    tactic_service.update_order_state(id, remark, model.ORDER_STATE_NEW)
    return jsonify(ApiResp().to_dict())

@app.post('/orders/done')
def done_order():
    data = request.json
    id = data.get('id')
    remark = data.get('remark')
    tactic_service.update_order_state(id, remark, model.ORDER_STATE_DONE)
    return jsonify(ApiResp().to_dict())


@app.post('/order/analysis')
def analyse():
    data = request.json
    id = data.get('id')
    p1 = data.get('p1')
    p2 = data.get('p2')
    if not p1:
        p1 = 3
    else:
        p1 = int(p1)
    if not p2:
        p2 = 5
    else:
        p2 = int(p2)
    ret = tactic_service.analyse_order(id, p1, p2)
    return jsonify(ApiResp(data = ret).to_dict())


# 策略列表
@app.post('/tactics')
def tactics():
    return jsonify(ApiResp(data=tactic_service.get_tactics()).to_dict())

# 策略yan

# 将信号加入交易

# 行情数据

# 交易数据

if __name__ == '__main__':
    db.init(10)
    production()