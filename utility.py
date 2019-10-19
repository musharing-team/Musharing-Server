import json

def singleton(cls, *args, **kw):
    '''
    单例装饰器
    '''
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

def drop_id(obj):
    '''
    原址递归删除 list 中的对象里所有以 _id 为 key 的键值对。
    用来作用于 mongo 返回的对象，删除多余的ObjectId
    '''
    if isinstance(obj, (list, tuple)):
        for i in obj:
            drop_id(i)
    if isinstance(obj, dict):
        try:
            obj.pop("_id")
        except KeyError:
            pass
        for i in obj:
            drop_id(obj[i])
