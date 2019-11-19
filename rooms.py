import uuid
from room import *

# 单例装饰器
def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class Rooms (object):
    def __init__(self):
        self.namespace = uuid.uuid1()
        self.rooms = {}

    def get_next_gid(self):
        '''
        获取一个不重复的gid

        具体实现是：使用 Rooms 实例建立时的 uuid1 做 namespace, len(rooms) 做 name, 生成出来的 uuid3
        '''
        gid = uuid.uuid3(self.namespace, str(len(self.rooms)))
        return str(gid)

    def new_room(self):
        gid = self.get_next_gid()
        self.rooms[gid] = Room(gid)
        return gid

    def clear(self):
        '''
        清除空的房间，避免无效的内存占用
        '''
        for i in self.rooms:
            if len(self.rooms[i].get_members()) <= 0:
                self.rooms.pop(i)

    def get_count_rooms(self):
        """
        获取当前房间总数
        """
        return len(self.rooms)
