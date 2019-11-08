import json
import logging

from flask import app, Flask, request, render_template

from notice import *
from rooms import *
from user_util import *
from playlist_util import *
from authenticate_util import AuthenticateUtil
from response_util import *
from notice_util import *
from utility import *

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
nu = NoticeUtil()
pu = PlaylistUtil()
au = AuthenticateUtil(uu, rooms)

@app.route('/')
def hello():
    return "Hello, musharing!"


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    如果收到 POST 请求，则尝试注册，
    登录成功，则返回一个 uid, name(encoded), img 组成的json
    '''
    try:
        assert request.method == 'POST', "method should be POST"

        name = None
        password = None
        img = None
        try:
            name = request.form["name"]
            password = request.form["password"]
            img = request.form["img"]
        except KeyError:
            raise RequestError("not enough param")
        
        user = uu.register(name, password, img)
        assert isinstance(user, User), "get user failed"
        
        logging.info('<register>: success. uid = %s' % user.uid)
        return response_success(get_single_user_content(user))

    except UserNameError as e:
        logging.warning('<register>: name_occupied. name = %s' % e.from_user)
        return response_error(get_simple_error_content(ResponseError.name_occupied))

    except Exception as e:
        logging.error('<register>: unexpected. request = %s, request.form = %s' % (request, request.form))
        return response_unexpected(e)


@app.route("/login", methods=['GET', 'POST'])
def login():
    '''
    如果收到 POST 请求，则尝试登录，
    登录成功，则返回一个 uid, name(encoded), img 组成的json
    '''
    try:
        assert request.method == 'POST', "method should be POST"

        name = None
        password = None
        try:
            name = request.form["name"]
            password = request.form["password"]
        except KeyError:
            raise RequestError("not enough param")

        user = uu.login(name, password)
        assert isinstance(user, User), "get user failed"
        uu.login_switch(user.uid, True)

        logging.info('<login>: success. uid = %s' %  user.uid)
        return response_success(get_single_user_content(user))

    except PasswordError as e:
        logging.warning('<login>: wrong_password. name = %s' % e.from_user)
        return response_error(get_simple_error_content(ResponseError.wrong_password))

    except UserNameError as e:
        logging.warning('<login>: wrong_name. name = %s' % e.from_user)
        return response_error(get_simple_error_content(ResponseError.wrong_name))

    except Exception as e:
        logging.error('<login>: unexpected. request = %s, request.form = %s' % (request, request.form))
        return response_unexpected(e)


@app.route('/attend', methods=["GET", "POST"])
def attend():
    '''
    已登陆的用户加入 Room
    '''
    def operate(from_uid, target_name):
        # 目标用户验证
        if not au.byName.exist(target_name):
            logging.warning('<attend>: target_not_exist. from_uid = %s, target_name = %s' %  (from_uid, target_name))
            return response_error(get_simple_error_content(ResponseError.target_not_exist))

        if not au.byName.logined(target_name):
            logging.warning('<attend>: target_not_login. from_uid = %s, target_name = %s' %  (from_uid, target_name))
            return response_error(get_simple_error_content(ResponseError.target_not_login))

        if au.byName.inroom(target_name):
            logging.warning('<attend>: target_in_room. from_uid = %s, target_name = %s' %  (from_uid, target_name))
            return response_error(get_simple_error_content(ResponseError.target_in_room))
        
        # 验证通过，可以添加
        from_user_data = uu.query_by_uid(from_uid)
        target_user_data = uu.query_by_name(target_name)

        par = lambda data: (data['uid'], data['name'], data['img'])

        from_par = par(from_user_data)
        target_par = par(target_user_data)

        if au.byUid.inroom(from_uid):   # 发起用户已经在 Room 中，把目标用户拉进去
            gid = from_user_data['group']
            uu.group_change(target_user_data['uid'], gid)
            rooms.rooms[gid].add_user(*target_par)
        else:   # 发起用户未处于 Room 中，新建并加入
            gid = rooms.new_room()
            uu.group_change(from_user_data['uid'], gid)
            rooms.rooms[gid].add_user(*from_par)
            uu.group_change(target_user_data['uid'], gid)
            rooms.rooms[gid].add_user(*target_par)
                        
        logging.info('<attend>: success. %s :+ %s -> %s' % (from_uid, target_user_data['uid'], gid))
        return response_success(get_simple_success_content("attend"))

    return common_login_auth_response("attend", request, operate, ("from_uid", "target_name"))
        

@app.route('/members', methods=["GET", "POST"])
def members():
    '''
    已登陆且身处 Room 的用户查询 Room 中的其他成员用户
    '''
    def operate(from_uid):
        from_user_data = uu.query_by_uid(from_uid)
        member_list = rooms.rooms[from_user_data['group']].get_members()

        logging.info('<members>: success. from_uid = %s' %  from_uid)
        return response_success({"members": member_list})

    return common_inroom_auth_response("members", request, operate, ("from_uid",))


@app.route("/send", methods=['GET', 'POST'])
def send():
    '''
    已登陆且身处 Room 的用户发送信息
    '''
    def operate(from_uid, msg):
        from_user_data = uu.query_by_uid(from_uid)
        rooms.rooms[from_user_data['group']].send_msg(from_uid, msg)

        logging.info('<send>: success. from_uid = %s' %  from_uid)
        return response_success(get_simple_success_content("send"))

    return common_inroom_auth_response("send", request, operate, ("from_uid", "msg"))


@app.route("/receive", methods=['GET', 'POST'])
def receive():
    '''
    已登陆且身处 Room 的用户检收新消息
    '''
    def operate(from_uid):
        from_user_data = uu.query_by_uid(from_uid)
        message_list = rooms.rooms[from_user_data['group']].receive_msg(from_uid)

        logging.info('<receive>: success. size = %s; from_uid = %s' %  (len(message_list), from_uid))
        return response_success({"messages": message_list})

    return common_inroom_auth_response("receive", request, operate, ("from_uid",))


@app.route("/leave", methods=['GET', 'POST'])
def leave():
    '''
    已登陆且身处 Room 的用户退出**Room**

    注意不是退出登录！
    '''
    def operate(from_uid):
        from_user_data = uu.query_by_uid(from_uid)
        uu.group_change(from_uid, None)
        rooms.rooms[from_user_data['group']].remove_user(from_uid)

        logging.info("<leave> success. {gid} -= {uid}".format(gid=from_user_data['group'], uid=from_uid))
        return response_success(get_simple_success_content("leave"))
    
    return common_inroom_auth_response("leave", request, operate, ("from_uid",))


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    '''
    已登陆的用户退出登录
    '''
    def operate(from_uid):
        from_user_data = uu.query_by_uid(from_uid)

        if au.byUid.inroom(from_uid):   # 用户加入了 Room，要先退出 Room，再退出登录
            uu.group_change(from_uid, None)
            rooms.rooms[from_user_data['group']].remove_user(from_uid)
            logging.info("<leave-when-logout> success. {gid} -= {uid}".format(gid=from_user_data['group'], uid=from_uid))
        
        uu.login_switch(from_uid, False)

        logging.info('<logout>: success. from_uid = %s' %  from_uid)
        return response_success(get_simple_success_content("logout"))
    
    return common_login_auth_response("logout", request, operate, ("from_uid",))


@app.route("/playlist", methods=['GET', 'POST'])
def playlist():
    '''
    已登陆且身处 Room 的用户获取播放列表
    '''
    def operate(from_uid, playlist_id):
        content = pu.get_playlist(playlist_id)
        if content != None:
            logging.info("<playlist> success. playlist_id = %s, from_uid = %s" % (playlist_id, from_uid))
            return response_success(content)
        else:
            logging.warning('<playlist> playlist_not_exist. playlist_id = %s, from_uid = %s' % (playlist_id, from_uid))
            return response_error(get_simple_error_content(ResponseError.playlist_not_exist))

    return common_inroom_auth_response("playlist", request, operate, ("from_uid", "playlist_id"))


@app.route("/category", methods=['GET', 'POST'])
def category():
    '''
    已登陆且身处 Room 的用户获取 播放列表的目录(被叫做 categoryList 😂)
    '''
    def operate(from_uid):
        content = pu.get_index()
        if content != None:
            logging.info("<category> success. from_uid = %s" % from_uid)
            return response_success({"categories": content})
        else:
            logging.warning('<category> fail_to_get_index. from_uid = %s' % from_uid)
            return response_error(get_simple_error_content(ResponseError.fail_to_get_index))

    return common_inroom_auth_response("category", request, operate, ("from_uid",))


@app.route("/notice", methods=['GET', 'POST'])
def notice():
    """
    用户 GET 收取通知，或管理员 POST 发送通知
    """
    try:
        if request.method == "GET":     # 用户获取通知
            from_uid = request.args.get("from_uid", None)
            notice_list = nu.get(from_uid)

            logging.info("<notice GET> success. from_uid = %s" % from_uid)
            return response_success({"notices": notice_list})

        elif request.method == "POST":    # 管理员发送通知
            name = request.form["name"]
            password = request.form["password"]

            if au.admin.isAdmin(name, password):
                notice = Notice().from_dict(dict(request.form))
                nu.add(notice)

                logging.info("<notice POST> success. name = %s" % name)
                return response_success(get_simple_success_content("notice"))
            else:
                logging.warning("<notice POST> not_permitted. name = %s, password = %s" % (name, password))
                return response_error(get_simple_error_content(ResponseError.not_permitted))
                
    except Exception as e:
        logging.error('<{name}>: unexpected. request = {request}, request.args = {r_args}, request.form = {form}'.format(
            name="notice", request=request, r_args=request.args, form=request.form))
        return response_unexpected(e)



def common_inroom_auth_response(name, request, operate, op_args):
    '''
    > 通用的需要通过验证用户存在、已登录、身处 Room 的操作。

    参数：
    - name: 操作名，用于日志输出；
    - request: Flask 传来的 request；
    - operate: 具体的操作函数，参数为需要从 request.form 中提取的值，返回值为成功后的response json;
    - op_args: operate 函数的 参数名 str 组成的列表。

    返回：response json

    说明:

    这个函数会从 request.form 中提取 from_uid 以及 op_args 中指定的所有值，若没有对应的值，会返回 unexpected；
    然后该函数会对用户是否 exist、login、inRoom  进行检测，若有不满足，返回 from_not_exist，from_not_login 或 from_not_in_room；
    通过了所有验证后，将调用 operate 函数，并用 argument unpacking 的方法把解析得到的 args 传给 operate。
    '''
    try:
        assert request.method == 'POST', "method should be POST"
        assert isinstance(op_args, (tuple, list)), "op_args should be tuple or list"

        from_uid = None
        args = {}
        try:
            from_uid = request.form["from_uid"]
            for i in op_args:
                args[i] = request.form[i]
        except KeyError:
            raise RequestError("not enough param")

        # 发起用户验证
        if not au.byUid.exist(from_uid):
            logging.critical('<{name}>: from_not_exist. from_uid = {from_uid}'.format(name=name, from_uid=from_uid))
            return response_error(get_simple_error_content(ResponseError.from_not_exist))

        if not au.byUid.logined(from_uid):
            logging.error('<{name}>: from_not_login. from_uid = {from_uid}'.format(name=name, from_uid=from_uid))
            return response_error(get_simple_error_content(ResponseError.from_not_login))

        if not au.byUid.inroom(from_uid):
            logging.error('<{name}>: from_not_in_room. from_uid = {from_uid}'.format(name=name, from_uid=from_uid))
            return response_error(get_simple_error_content(ResponseError.from_not_in_room))

        # 通过验证，可以操作
        return operate(**args)

    except Exception as e:
        logging.error('<{name}>: unexpected. request = {request}, request.form = {form}'.format(
            name=name, request=request, form=request.form))
        return response_unexpected(e)


def common_login_auth_response(name, request, operate, op_args):
    '''
    > 通用的需要通过验证用户存在、已登录的操作。

    参数：
    - name: 操作名，用于日志输出；
    - request: Flask 传来的 request；
    - operate: 具体的操作函数，参数为需要从 request.form 中提取的值，返回值为成功后的response json;
    - op_args: operate 函数的 参数名 str 组成的列表。

    返回：response json

    说明:

    这个函数会从 request.form 中提取 from_uid 以及 op_args 中指定的所有值，若没有对应的值，会返回 unexpected；
    然后该函数会对用户是否 exist、login、inRoom  进行检测，若有不满足，返回 from_not_exist，from_not_login 或 from_not_in_room；
    通过了所有验证后，将调用 operate 函数，并用 argument unpacking 的方法把解析得到的 args 传给 operate。

    '''
    try:
        assert request.method == 'POST', "method should be POST"
        assert isinstance(op_args, (tuple, list)), "op_args should be tuple or list"

        from_uid = None
        args = {}
        try:
            from_uid = request.form["from_uid"]
            for i in op_args:
                args[i] = request.form[i]
        except KeyError:
            raise RequestError("not enough param")

        # 发起用户验证
        if not au.byUid.exist(from_uid):
            logging.critical('<{name}>: from_not_exist. from_uid = {from_uid}'.format(name=name, from_uid=from_uid))
            return response_error(get_simple_error_content(ResponseError.from_not_exist))

        if not au.byUid.logined(from_uid):
            logging.error('<{name}>: from_not_login. from_uid = {from_uid}'.format(name=name, from_uid=from_uid))
            return response_error(get_simple_error_content(ResponseError.from_not_login))

        # 通过验证，可以操作
        return operate(**args)

    except Exception as e:
        logging.error('<{name}>: unexpected. request = {request}, request.form = {form}'.format(
            name=name, request=request, form=request.form))
        return response_unexpected(e)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
