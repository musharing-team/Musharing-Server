'''

# 使用

创建一个 UserUtil 实例，然后，可以通过 该实例调用方法。

使用可以参考 该模块中的 test 函数。

## 方法

register: 注册
login: 登录
next_uid: 获取id
encode_name: 获取名字的 base64
decode_name: 解码 base64
calc_password: 计算密码 md5

# 实现

用户数据库使用 mongoDB

### 单条数据样式

```
{
    "uid": "ID_INT",
    "name": "NAME_BASE64",
    "password": "PASSWORD_MD5"
    "img": "IMG_URI"
    "login": "True_OR_False"
    "group": "GID_OR_None"
}
```

用户唯一ID用自增整数
用户名用 Base64 转码储存
密码用 用户名Base64 加盐后 md5 加密储存 (**通过 hmac 算法**)
图片储存在服务器磁盘里，数据库里存URI

login 字段标示出用户当前是否已登录（视为在线）
group 表示用户是否已经加入了聊天，是则写明GID，否则为 "None"

## 维护说明

关于 pymongo 的相关事宜，在后期维护、升级的过程中（尤其是修改为多线程的时候！）要注意参考：[PyMongo 常见问题](https://juejin.im/post/5a3b1e9c51882515945abedf)。

# TODO

用户名、密码的修改，以及连续尝试次数的限制。

'''

import pymongo
import base64
import hmac

from utility import singleton
from user import *


# 错误类
class RequestError(ValueError):
    def __init__(self, from_user=""):
        self.from_user = from_user
        super()


class UserNameError(RequestError):
    def __init__(self, from_user=''):
        super().__init__(from_user=from_user)


class PasswordError(RequestError):
    def __init__(self, from_user=''):
        super().__init__(from_user=from_user)


class UidError(RequestError):
    def __init__(self, from_user=''):
        super().__init__(from_user=from_user)


# 特殊 User 对象
chatbot_user = User("chatbot", "chatbot", "https://cdn.pixabay.com/photo/2017/12/03/14/31/kawaii-2995014__480.png")


# UserUtil 单例化
@singleton
class UserUtil (object):
    def __init__(self):
        # 数据库名
        self.DATABASE_NAME = "musharing"
        self.COLLECTION_NAME = "users"

        # 连接数据库
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client[self.DATABASE_NAME]
        self.collection = self.db[self.COLLECTION_NAME]

    def next_uid(self):
        '''
        获取为新用户分配的 uid
        '''
        # 获取当前用户总数
        count = self.collection.count_documents({})
        return str(count + 1)

    def query_by_uid(self, uid):
        '''
        通过 uid 查找用户
        若用户存在，返回目标用户的{uid, name, img, login, group}，否则 raise 一个 UidError
        '''
        result = self.collection.find_one({"uid": uid})
        if result != None:
            data = {
                "uid": result["uid"],
                "name": result["name"],
                "img": result["img"],
                "login": result["login"],
                "group": result["group"]
            }
            return data
        else:
            raise UidError(uid)

    def query_by_name(self, name):
        '''
        通过用户名查找用户
        若用户存在，返回目标用户的{uid, name, img, login, group}，否则 raise 一个 UserNameError
        '''
        result = self.collection.find_one({"name": name})
        if result != None:
            data = {
                "uid": result["uid"],
                "name": result["name"],
                "img": result["img"],
                "login": result["login"],
                "group": result["group"]
            }
            return data
        else:
            raise UserNameError(name)

    def login(self, name, password):
        '''
        用户登录，成功则返回尝试登录用户的 User 实例，否则 raise UserNameError or PasswordError

        传过来的 name 是 base64 编码过的 str
        password 是 hmac 后的 str
        '''
        # 查询用户
        result = self.collection.find_one({'name': name})
        if result != None:  # 有这个用户
            # 比对密码
            if result["password"] == password:  # 密码正确，登录成功，返回对应的用户对象
                user = User(result["uid"], result["name"], result["img"])
                return user
            else:   # 密码不正确，释放一个密码错误
                raise PasswordError(name)
        else:   # result == None，没有该用户，释放一个用户名错误
            raise UserNameError(name)

    def register(self, name, password, img_url):
        '''
        新用户注册，成功则返回尝试注册用户的 User 实例，否则（用户名已存在） raise 一个 UserNameError

        传过来的 name 是 base64 编码过的 str
        password 是 hmac 后的 str
        '''
        # 查看用户是否已经存在
        exist = self.collection.find_one({'name': name})
        if exist == None:   # 没有这个用户，新建
            user_data = {
                "uid": self.next_uid(),
                "name": name,
                "password": password,
                "img": img_url,
                "login": "False",
                "group": "None"
            }
            self.collection.insert_one(user_data)
            return self.login(name, password)   # 成功则返回尝试注册用户的 User 实例

        else:   # 用户已经存在，释放一个用户名错误
            raise UserNameError(name)

    def login_switch(self, uid, state):
        '''
        标示用户登录与否
        将数据库中用户(uid)的 login 字段修改为 state

        state 的值应该为 True or False
        '''
        condition = {"uid": uid}
        user_data = self.collection.find_one(condition)
        user_data['login'] = str(state)
        self.collection.update_one(condition, {"$set": user_data})
        
    def group_change(self, uid, gid):
        '''
        标示用户是否加入了 musharing_ser
        将数据库中用户(uid)的 group 字段修改为 state

        gid 的值为 gid (str) or None
        '''
        condition = {"uid": uid}
        user_data = self.collection.find_one(condition)
        user_data['group'] = str(gid)
        self.collection.update_one(condition, {"$set": user_data})

    def get_count_all(self):
        """
        获取用户总数
        """
        return self.collection.count_documents({})

    def get_count_login(self):
        """
        获取当前登录状态为 True 的人的总数
        """
        return self.collection.count_documents({"login": str(True)})

    def get_count_inroom(self):
        """
        获取当前状态为在房间中的人的总数
        """
        return self.collection.count_documents({"group": {'$ne': str(None)}})

    @staticmethod
    def encode_name(name_str):
        name_encode =  base64.b64encode(name_str.encode("utf-8"))
        return name_encode.decode("utf-8")

    @staticmethod
    def decode_name(name_base64):
        name_decode = base64.b64decode(name_base64.encode("utf-8"))
        return name_decode.decode("utf-8")

    @staticmethod
    def calc_password(name_base64, password):
        uid_bytes = name_base64.encode("utf-8")
        password_bytes = password.encode("utf-8")
        h = hmac.new(uid_bytes, password_bytes, digestmod="MD5")
        encoded_password = h.hexdigest()
        return encoded_password

# def test():
#     uu = UserUtil()
    
#     name = "foo"
#     passwd = "foobar"

#     ne = uu.encode_name(name)
#     pe = uu.calc_password('1', passwd)

#     print(ne)
#     print(pe)

#     user1 = user2 = user3 = user4 = user5 = None

#     print("* bad username login:")
#     try:
#         user1 = uu.login(ne, pe)
#     except UserNameError:
#         print("无此用户")
#     except PasswordError:
#         print("密码错误")
#     print(user1)

#     print("* register:")
#     try:
#         user2 = uu.register(ne, pe, "/img")
#     except UserNameError:
#         print("已有此用户")
#     except PasswordError:
#         print("Unexpected: 密码错误!!!!!!!!")
#     print(user2)

#     print("* bad register:")
#     try:
#         user3 = uu.register(ne, "A Bad Password", "/img")
#     except UserNameError:
#         print("已有此用户")
#     except PasswordError:
#         print("Unexpected: 密码错误!!!!!!!!")
#     print(user3)

#     print("* normal login:")
#     try:
#         user4 = uu.login(ne, pe)
#     except UserNameError:
#         print("无此用户")
#     except PasswordError:
#         print("密码错误")
#     print(user4)

#     print("* bad password login:")
#     try:
#         user5 = uu.login(ne, "A Bad Password")
#     except UserNameError:
#         print("无此用户")
#     except PasswordError:
#         print("密码错误")
#     print(user5)

# if __name__ == "__main__":
#     test()
