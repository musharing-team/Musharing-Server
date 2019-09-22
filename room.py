from user import *
from group import *

class Room (object):
    '''
    聊天室类，封装 User 和其集合 Group
    实现对外界的接口
    支持分布式进程的实现
    '''

    def __init__(self, gid):
        # TODO: Group 的 gid 的分配、获取
        self.group = Group(gid)

    def add_user(self, user_id, user_name, user_img):
        user = User(user_id, user_name, user_img)
        self.group.append(user)
        return True

    def remove_user(self, user_id):
        if user_id in self.group.members:
            user = self.group.members[user_id]
            self.group.remove(user)
            return True
        return False
    
    def send_msg(self, from_user_id, msg):
        if from_user_id in self.group.members:
            user = self.group.members[from_user_id]
            user.send(msg)
            return True
        return False

    def receive_msg(self, user_id):
        if user_id in self.group.members:
            user = self.group.members[user_id]
            msg_list = []
            msg = user.next_msg()
            while msg != None:          # 一次性把全部都取出来
                msg_list.append(msg)
                msg = user.next_msg()
            return msg_list
        return []

    def get_members(self):
        '''
        要获取一个让前端用户可见的成员列表
        '''
        members = []
        for i in self.group.members.values():
            members.append(i.get_user_data())
        return members
