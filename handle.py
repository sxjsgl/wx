import hashlib
import re
import time
from pwd_keeper import *


def wx_check_signature(request):
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    if not all([signature, timestamp, nonce]):
        print(signature)
        return ''

    token = '123456'
    temp = [token, timestamp, nonce]
    temp.sort()
    temp = ''.join(temp)
    sha1 = hashlib.sha1()
    sha1.update(temp.encode('utf-8'))
    hashcode = sha1.hexdigest()
    if hashcode == signature:
        print(hashcode)
        return hashcode
    else:
        print('other')
        return ''


def wx_make_reply(request):
    xml_data = request.data.decode('utf-8')
    print(xml_data)
    fromuser = re.search('<ToUserName><!\[CDATA\[(.*)\]\]></ToUserName>', xml_data).group(1)
    touser = re.search('<FromUserName><!\[CDATA\[(.*)\]\]></FromUserName>', xml_data).group(1)
    msgtype = re.search('<MsgType><!\[CDATA\[(.*)\]\]></MsgType>', xml_data).group(1)
    createtime = int(time.time())
    if msgtype == 'text':
        content = wx_pipeline_other(touser, re.search('<Content><!\[CDATA\[(.*)\]\]></Content>', xml_data, flags=re.S).group(1))
        print(content)
    if msgtype == 'image':
        content = re.search('<MediaId><!\[CDATA\[(.*)\]\]></MediaId>', xml_data).group(1)
        print('图片消息')

    return {'touser': touser, 'fromuser': fromuser, 'createtime': createtime, 'msgtype': msgtype, 'content': content}


def wx_pipeline_other(user, message):
    if message == '密码':
        temp = []
        temp += ["操作示例："]
        temp += ["添加记录：add_record(target, account='332', pwd=None, note='none', letter=False, spcl=False, length=8)"]
        temp += ["删除记录：del_record(target)"]
        temp += ["更改记录：chg_record(target, account=None, pwd=None, note=None, letter=False, spcl=False, length=8)"]
        temp += ["查询记录：srch_record(target=None)"]
        temp += ["\ntarget:目标网站\naccount:账号\npwd:密码,如果想自动生成密码可以不输入.length表示自动生成的密码长度,默认只有数字,letter是否包含字母,spcl是否包含特殊字符\nnote:备注"]
        return '\n'.join(temp)

    pwd_cmd = re.search('(.*_record)\(.*\)', message)
    if pwd_cmd:
        if pwd_cmd.group(1) in ['add_record', 'del_record', 'chg_record', 'srch_record']:
            base = pwd_base(user)
            exec_scope = dict(locals())
            exec("temp =  base." + pwd_cmd.group(0), exec_scope)
            return exec_scope['temp']

    return 'reply: ' + message


if __name__ == '__main__':
    a = wx_pipeline_other('s-x', "add_record('ali')")
    print(a)
