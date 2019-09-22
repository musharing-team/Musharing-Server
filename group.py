class Group (object):
    '''
    群组类，用来表示同一个聊天室里的用户集合
    处理用户消息的广播分发
    '''

    def __init__(self, group_id):
        self.gid = group_id
        self.members = {}

    def append(self, user):
        if user.uid not in self.members:
            self.members[user.uid] = user
            user.attend(self)

    def remove(self, user):
        if user.uid in self.members:
            self.members.pop(user.uid)
            user.logout()

    def send(self, msg):
        for member in self.members.values():
            member.receive(msg)
