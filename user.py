class User (object):
    '''
    用户类，用还表示一个**登录**后的用户
    实现消息的发送、获取的接口
    '''

    def __init__(self, user_id, user_name, user_img):
        self.uid = user_id
        self.name = user_name
        self.img = user_img

        self.group = None
        self.unhandled_msg = []

    def attend(self, group):
        if self.group != group:
            self.group = group
            group.append(self)

    def logout(self):
        if self.group != None:
            temp_group = self.group
            self.group = None
            temp_group.remove(self)

    def send(self, msg):
        if self.group:
            self.group.send(msg)
        else:
            raise ValueError("User belong to no group.")

    def receive(self, msg):
        self.unhandled_msg.append(msg)

    def next_msg(self):
        msg = None
        if len(self.unhandled_msg) > 0:
            msg = self.unhandled_msg.pop(0)     # FIFO
        return msg

    def get_user_data(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'img': self.img
        }
