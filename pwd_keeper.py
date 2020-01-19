import string
import sqlite3
import random
import base64


class pwd_base:
    file = 'pwd.db'
    user = ''

    def __init__(self, user):
        self.user = user.replace('-', 'a')
        self.conn = sqlite3.connect(self.file)
        self.cursor = self.conn.cursor()
        if (self.user,) not in self.cursor.execute(
                'select name from sqlite_master where type="table" order by name').fetchall():
            self.cursor.execute(
                "create table " + self.user + " (target varchar(40) primary key, account varchar(20), pwd varchar(256), note varchar(1024))")
            self.conn.commit()

    def __del__(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def add_record(self, target, account='none', pwd=None, note='none', letter=False, spcl=False, length=8):
        if not pwd:
            pwd = pwd_gen(letter=letter, spcl=spcl, length=length)
        try:
            self.cursor.execute("insert into " + self.user + " values (?, ?, ?, ?)", (target, account, encrypt(pwd), encrypt(note)))
            self.conn.commit()
            return '添加记录成功'
        except sqlite3.IntegrityError as e:  # unique异常
            return '已经存在记录，请先查询然后决定是否更改记录'
        except sqlite3.OperationalError as e:  # 没有此数据库
            return '添加记录失败'

    def del_record(self, target):
        try:
            temp = self.cursor.execute("delete from " + self.user + " where target=?", (target,))
            if temp.rowcount:
                self.conn.commit()
                return '删除记录成功'
            else:
                return '没有此条记录，删除记录失败'
        except sqlite3.OperationalError as e:  # 没有此数据库
            return '删除记录失败'

    def chg_record(self, target, account=None, pwd=None, note=None, letter=False, spcl=False, length=8):
        try:
            temp = []
            if account:
                temp += [" account='" + account + "'"]
            if account and not pwd:
                pwd = pwd_gen(letter=letter, spcl=spcl, length=length)
            if pwd:
                temp += [" pwd='" + encrypt(pwd) + "'"]
            if note:
                temp += [" note='" + encrypt(note) + "'"]
            str_cmd = "update " + self.user + " set" + ','.join(temp) + " where target='" + target + "'"
            temp = self.cursor.execute(str_cmd)
            self.conn.commit()
            if temp.rowcount:
                return "更改记录成功"
            else:
                return "更改记录失败"
        except sqlite3.OperationalError as e:  # 没有此数据库
            return '更改记录失败'

    def srch_record(self, target=None):
        try:
            if not target:
                res = self.cursor.execute("select * from " + self.user).fetchall()
            else:
                res = self.cursor.execute("select * from " + self.user + " where target=?", (target,)).fetchall()
            res = ["目标："+str(d[0])+" 账号："+str(d[1])+" 密码："+decrypt(d[2])+" 备注："+decrypt(d[3]) for d in res]
            if res:
                return "\n".join(res)
            else:
                return '数据库为空,请先添加记录'
        except sqlite3.OperationalError as e:  # 没有此数据库
            return '查询数据库失败'


def pwd_gen(letter=False, spcl=False, length=8):
    password = []
    temp = random.sample(range(1, length), 2)
    temp.sort()
    password += random.choices(string.digits, k=temp[0])
    password += random.choices(string.ascii_lowercase if letter else string.digits, k=temp[1] - temp[0])
    password += random.choices(''.join(['!', '#', '$', '&', '=']) if spcl else string.digits, k=length - temp[1])
    random.shuffle(password)
    password = ''.join(password)

    return password


def encrypt(text):
    return base64.b64encode(text.encode()).decode()


def decrypt(text):
    return base64.b64decode(text.encode()).decode()


if __name__ == '__main__':
    base = pwd_base('test_db')
    base.add_record('ali', letter=True)
    temp = base.chg_record('ali', note='test')
    print(temp)