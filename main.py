import json
from flask import Flask, render_template, request, redirect, make_response
from handle import *
app = Flask(__name__)


@app.route('/wx', methods=['GET', 'POST'])
def wx_get():
    fromwx = wx_check_signature(request)
    if fromwx:
        print('来自微信')
        if request.method == 'GET':
            print('微信校验')
            return fromwx
        else:
            print('用户消息')
            temp = render_template('wx_reply_template.xml', info=wx_make_reply(request))
            print(temp)
            return temp
    else:
        print('不是微信消息')
        return '别乱搞'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)



