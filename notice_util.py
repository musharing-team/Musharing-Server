import pymongo

from notice import Notice
from utility import singleton

@singleton
class NoticeUtil (object):
    """
    """

    def __init__(self):
        # 连接数据库
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client["musharing"]
        self.collection = self.db["notices"]

    def add(self, notice: Notice):
        # self.collection.insert_one(notice.to_dict())
        assert notice.is_empty() == False
        self.update(notice)

    def get(self, uid=None):
        """
        获取通知，传入 uid: str 来指定获取用于指定用户的通知，缺省 uid=None 获取所有通知
        """
        notices = []
        for r in self.collection.find() or []:
            n = Notice().from_dict(r)
            if n.is_expired():
                self.drop_expired(n)
            if uid == None or n.is_for_user(uid):
                notices.append(n.dumps())
        return notices

    def update(self, notice: Notice):
        assert notice.is_empty() == False

        # 存在则更新，不存在则新建
        self.collection.update_one(
            {'nid': notice.nid},
            {'$set': notice.to_dict()},
            upsert=True
            )

    def drop_expired(self, notice=None):
        if isinstance(notice, Notice):
            self.collection.delete_one({"nid": notice.nid})
        else:
            for r in self.collection.find() or []:
                n = Notice().from_dict(r)
                if n.is_expired():
                    self.drop_expired(n)

    def clean_all(self):
        self.collection.delete_many({})
