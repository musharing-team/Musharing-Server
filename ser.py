import json
import logging

from flask import app, Flask, request, render_template

from rooms import *
from user_util import *
from playlist import *

# 日志配置
logging.basicConfig(level=logging.DEBUG,
                format='[%(levelname)s] %(asctime)s %(filename)s[line:%(lineno)d] %(message)s',
                filename='musharing_server.log',
                filemode='a')
# 定义一个StreamHandler，将 WARNING 或更高级别的日志信息打印到标准错误，并将其添加到当前的日志处理对象
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(filename)s[line:%(lineno)d] %(message)s')
console.setFormatter(formatter)
logging.getLogger('musharing_server').addHandler(console)
# 日志调用： logging.<debug, info, warning, error, critical>('msg')

app = Flask(__name__)

rooms = Rooms()
uu = UserUtil()

@app.route('/')
def hello():
    return "Hello, musharing!"


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    如果收到 POST 请求，则尝试注册，
    登录成功，则返回一个 uid, name(encoded), img 组成的json
    '''
    if request.method == 'POST':
        name = request.form["name"]
        password = request.form["password"]
        img = request.form["img"]
        try:
            user = uu.register(name, password, img)
            if isinstance(user, User):
                data = {
                    "uid": user.uid,
                    "name": uu.encode_name(user.name),
                    "img": user.img
                }
                logging.info('<register>: Successfully register. Uid = %s' % user.uid)
                return json.dumps(data)
        except UserNameError:
            logging.warning('<register>: Try to regist with a existing UserName. username = %s' % name)
            data = {
                "error": "UserNameError"
            }
            return json.dumps(data)
    logging.error('<register>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"})


@app.route("/login", methods=['GET', 'POST'])
def login():
    '''
    如果收到 POST 请求，则尝试登录，
    登录成功，则返回一个 uid, name(encoded), img 组成的json
    '''
    if request.method == 'POST':
        name = request.form["name"]
        password = request.form["password"]
        try:
            user = uu.login(name, password)
            if isinstance(user, User):
                uu.login_switch(user.uid, True)     # 在数据库中标记为已登录
                data = {
                    "uid": user.uid,
                    "name": uu.encode_name(user.name),
                    "img": user.img
                }
                logging.info('<login>: Successfully login. Uid = %s' %  user.uid)
                return json.dumps(data)
        except PasswordError:
            data = {
                "error": "PasswordError"
            }
            logging.warning('<login>: Try to login with a bad Password. username = %s' % name)
            return json.dumps(data)
        except UserNameError:
            data = {
                "error": "UserNameError"
            }
            logging.warning('<login>: Try to login with a bad UserName. username = %s' % name)
            return json.dumps(data)
    logging.error('<login>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"})


@app.route('/attend', methods=["GET", "POST"])
def attend():
    '''
    已登陆的用户加入 Room
    '''
    if request.method == 'POST':
        from_uid = request.form["from_uid"]
        target_name = request.form["target_name"]
        try:
            from_user_data = uu.query_by_uid(from_uid)
            target_user_data = uu.query_by_name(target_name)
            if from_user_data['login'] != str(True):    # 发起用户未登录
                logging.error('<attend> A NO LOGIN USER TRY TO attend. request.form = %s' % request.form)
                data = { "error": "UserNotLogin" }
            else:   # 发起用户登录正常
                if target_user_data['login'] != str(True):  # 目标没有登录
                    logging.warning('<attend> Try to attend a not-login target-user. request.form = %s' % request.form)
                    data = { "error": "TargetUserNotLogin" }
                else:   # 目标用户有登录
                    if target_user_data['group'] != str(None):  # 目标用户已经加入了 Room
                        logging.warning('<attend> Try to attend a Already-In-Group target-user. request.form = %s' % request.form)
                        data = { "error": "TargetUserInGroup" }
                    else:   # 发起用户已登陆，目标用户已登录且没有加入 Room，可以建立连接
                        if from_user_data['group'] != str(None):    # 发起用户已经在 Room 中，把目标用户拉进去
                            gid = from_user_data['group']
                            uu.group_change(target_user_data['uid'], gid)
                            rooms.rooms[gid].add_user(target_user_data['uid'], target_user_data['name'], target_user_data['img'])
                        else:   # 发起用户未处于 Room 中，新建并加入
                            gid = rooms.new_room()
                            uu.group_change(from_user_data['uid'], gid)
                            rooms.rooms[gid].add_user(from_user_data['uid'], from_user_data['name'], from_user_data['img'])
                            uu.group_change(target_user_data['uid'], gid)
                            rooms.rooms[gid].add_user(target_user_data['uid'], target_user_data['name'], target_user_data['img'])
                        logging.info('<attend>: Successfully attend. %s :+ %s -> %s' % (from_uid, target_user_data['uid'], gid))
                        data = {"successful": "attend"}
            return json.dumps(data)
        except UserNameError:   # 目标用户不存在
            logging.warning('<attend>: Try to attend with a non-existing target user. request.form = %s' % request.form)
            return json.dumps({ "error": "UserNameError" })
        except UidError:    # 发起用户不存在
            logging.critical('<attend>: A NO EXISTING FROM-USER TRY TO attend. request.form = %s' % request.form)
            return json.dumps({ "error": "UidError" })
    logging.error('<attend>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"}) 
        

@app.route('/members', methods=["GET", "POST"])
def members():
    '''
    已登陆且身处 Room 的用户查询 Room 中的其他成员用户
    '''
    if request.method == 'POST':
        from_uid = request.form["from_uid"]
        try:
            from_user_data = uu.query_by_uid(from_uid)
            if from_user_data['login'] != str(True):    # 发起用户未登录
                logging.error('<member> A NO LOGIN USER TRY TO member. request.form = %s' % request.form)
                data = {"error": "UserNotLogin"}
            else:   # 发起用户登录正常
                if from_user_data['group'] == str(None):  # 用户未加入 Room
                    logging.warning('<member> A not in group user try to member. from_uid = %s' % from_uid)
                    data = {"error": "UserNotInGroup"}
                else:   # 发起用户已登陆，且加入了 Room，可以获取成员信息，在这里要对 userName base64 编码
                    mem_raw = rooms.rooms[from_user_data['group']].get_members()
                    mem = []
                    for i in mem_raw:
                        i['neme'] = uu.encode_name(i['name'])
                        mem.append(i)
                    data = {"members": mem}
                    '''
                    # 上面的代码也可以用 map 实现为原址的：
                    mem_raw = rooms.rooms[from_user_data['group']].get_members()
                    def encode(item):   # lambda 表达式里不能赋值，所以写成一个内嵌函数
                        item['name'] = uu.encode_name(i['name'])
                    list(map(encode, mem_raw))      # 这里外面要包一个list()才能原址改变 mem_raw，这个表达式的值是[None, ...]
                    data = {"members": mem_raw}
                    '''
                    logging.info('<member> Successfully member. gid = %s' % from_user_data['group'])
            return json.dumps(data)
        except UidError:    # 发起用户不存在
            logging.critical('<member>: A NO EXISTING FROM-USER TRY TO member. request.form = %s' % request.form)
            return json.dumps({ "error": "UidError" })
    logging.error('<member>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"})


@app.route("/send", methods=['GET', 'POST'])
def send():
    '''
    已登陆且身处 Room 的用户发送信息
    '''
    if request.method == 'POST':
        from_uid = request.form["from_uid"]
        msg = request.form["msg"]
        try:
            from_user_data = uu.query_by_uid(from_uid)
            if from_user_data['login'] != str(True):    # 发起用户未登录
                data = {"error": "UserNotLogin"}
                logging.error('<send> A NO LOGIN USER TRY TO send. request.form = %s' % request.form)
            else:   # 发起用户登录正常
                if from_user_data['group'] == str(None):  # 用户未加入 Room
                    data = {"error": "TargetUserNotInGroup"}
                    logging.warning('<send> A not in group user try to send. from_uid = %s' % from_uid)
                else:   # 发起用户已登陆，且加入了 Room，可以发送
                    rooms.rooms[from_user_data['group']].send_msg(from_uid, msg)
                    data = {"successful": "sent"}
                    logging.info('<send> Successfully send. Uid = %s' % from_uid)
            return json.dumps(data)
        except UidError:    # 发起用户不存在
            logging.critical('<send>: A NO EXISTING FROM-USER TRY TO send. request.form = %s' % request.form)
            return json.dumps({ "error": "UidError" })
    logging.error('<send>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"})


@app.route("/receive", methods=['GET', 'POST'])
def receive():
    '''
    已登陆且身处 Room 的用户检收新消息
    '''
    if request.method == 'POST':
        from_uid = request.form["from_uid"]
        try:
            from_user_data = uu.query_by_uid(from_uid)
            if from_user_data['login'] != str(True):    # 发起用户未登录
                data = {"error": "UserNotLogin"}
                logging.error('<receive> A NO LOGIN USER TRY TO receive. request.form = %s' % request.form)
            else:   # 发起用户登录正常
                if from_user_data['group'] == str(None):  # 用户未加入 Room
                    logging.warning('<receive> a not in group user try to receive. request.form = %s' % request.form)
                    data = {"error": "TargetUserNotInGroup"}
                else:   # 发起用户已登陆，且加入了 Room，可以发送
                    messages = rooms.rooms[from_user_data['group']].receive_msg(from_uid)
                    if len(messages) > 0:
                        logging.info('<receive> Successfully receive (%s messages). from_uid = %s' % (len(messages), from_uid))
                    data = {"messages": messages}
            return json.dumps(data)
        except UidError:    # 发起用户不存在
            logging.critical('<receive>: A NO EXISTING FROM-USER TRY TO receive. request.form = %s' % request.form)
            return json.dumps({ "error": "UidError" })
    logging.error('<receive>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"})


@app.route("/leave", methods=['GET', 'POST'])
def leave():
    '''
    已登陆且身处 Room 的用户退出**Room**

    注意不是退出登录！
    '''
    if request.method == 'POST':
        from_uid = request.form["from_uid"]
        try:
            from_user_data = uu.query_by_uid(from_uid)
            if from_user_data['login'] != str(True):    # 发起用户未登录
                logging.error('<leave> A NO LOGIN USER TRY TO leave. request.form = %s' % request.form)
                data = {"error": "UserNotLogin"}
            else:   # 发起用户登录正常
                if from_user_data['group'] == str(None):  # 用户未加入 Room
                    logging.warning('<leave> A not in group user try to leave. request.form = %s' % request.form)
                    data = {"error": "UserNotInGroup"}
                else:   # 发起用户已登陆，且加入了 Room，可以退出
                    uu.group_change(from_uid, None)
                    rooms.rooms[from_user_data['group']].remove_user(from_uid)
                    logging.info("<leave> Successfully leave. from_uid = %s" % from_uid)
                    data = {"successful": 'left'}
            return json.dumps(data)
        except UidError:    # 发起用户不存在
            logging.critical('<leave>: A NO EXISTING FROM-USER TRY TO leave. request.form = %s' % request.form)
            return json.dumps({ "error": "UidError" })
    logging.error('<leave>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"})


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    '''
    已登陆的用户退出登录
    '''
    if request.method == 'POST':
        from_uid = request.form["from_uid"]
        try:
            from_user_data = uu.query_by_uid(from_uid)
            if from_user_data['login'] != str(True):    # 发起用户未登录
                data = {"error": "UserNotLogin"}
                logging.error('<logout> A NO LOGIN USER TRY TO logout. request.form = %s' % request.form)
            else:   # 发起用户登录正常
                if from_user_data['group'] != str(None):  # 用户加入了 Room，要先退出 Room，再退出登录
                    uu.group_change(from_uid, None)
                    rooms.rooms[from_user_data['group']].remove_user(from_uid)
                # 发起用户已登陆，可以退出
                uu.login_switch(from_uid, False)
                logging.error('<logout> Successfully logout. from_uid = %s' % from_uid)
                data = {"successful": 'logout'}
            return json.dumps(data)
        except UidError:    # 发起用户不存在
            logging.critical('<logout>: A NO EXISTING FROM-USER TRY TO logout. request.form = %s' % request.form)
            return json.dumps({ "error": "UidError" })
    logging.error('<logout>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"})


@app.route("/playlist", methods=['GET', 'POST'])
def playlist():
    '''
    已登陆且身处 Room 的用户获取播放列表
    '''
    if request.method == 'POST':
        from_uid = request.form["from_uid"]
        playlist_id = request.form["playlist"]
        try:
            from_user_data = uu.query_by_uid(from_uid)
            if from_user_data['login'] != str(True):    # 发起用户未登录
                data = {"error": "UserNotLogin"}
                logging.error('<playlist> A NO LOGIN USER TRY TO playlist. request.form = %s' % request.form)
            else:   # 发起用户登录正常
                if from_user_data['group'] == str(None):  # 用户未加入 Room
                    logging.warning('<playlist> a not in group user try to playlist. request.form = %s' % request.form)
                    data = {"error": "TargetUserNotInGroup"}
                else:   # 发起用户已登陆，且加入了 Room，可以获取
                    content = get_playlist(playlist_id)
                    if content != None:
                        logging.info("<playlist> Successfully playlist. playlist_id = %s" % playlist_id)
                        data = content
                    else:
                        logging.warning('<playlist> try to get a no exist playlist. request.form = %s' % request.form)
                        data = {"error": "NoSuchPlaylist"}
            return json.dumps(data)
        except UidError:    # 发起用户不存在
            logging.critical('<playlist>: A NO EXISTING FROM-USER TRY TO playlist. request.form = %s' % request.form)
            return json.dumps({ "error": "UidError" })
    logging.error('<playlist>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"})


@app.route("/category", methods=['GET', 'POST'])
def category():
    '''
    已登陆且身处 Room 的用户获取 播放列表的目录(被叫做 categoryList 😂)
    '''
    if request.method == 'POST':
        from_uid = request.form["from_uid"]
        try:
            from_user_data = uu.query_by_uid(from_uid)
            if from_user_data['login'] != str(True):    # 发起用户未登录
                data = {"error": "UserNotLogin"}
                logging.error('<category> A NO LOGIN USER TRY TO category. request.form = %s' % request.form)
            else:   # 发起用户登录正常
                if from_user_data['group'] == str(None):  # 用户未加入 Room
                    logging.warning('<category> a not in group user try to category. request.form = %s' % request.form)
                    data = {"error": "TargetUserNotInGroup"}
                else:   # 发起用户已登陆，且加入了 Room，可以获取
                    content = get_index()
                    if content != None:
                        logging.info("<category> Successfully category. uid = %s" % from_uid)
                        data = content
                    else:
                        logging.warning('<category> try to get a no exist category. request.form = %s' % request.form)
                        data = {"error": "FailToGetIndex"}
            return json.dumps(data)
        except UidError:    # 发起用户不存在
            logging.critical('<category>: A NO EXISTING FROM-USER TRY TO category. request.form = %s' % request.form)
            return json.dumps({ "error": "UidError" })
    logging.error('<category>: Unexpected Error: request.method = %s, request.form = %s' % (request.method, request.form))
    return json.dumps({"error": "Unexpected"})


if __name__ == '__main__':
    app.run()
