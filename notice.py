class Notice (object):
    '''
    # 通知

    代表一条通知的类

    属性：

    - `nid: str` 通知的 id 识别码
    - `title: str` 通知标题
    - `content: str` 通知的具体内容
    - `expired: float` 通知过期的时间戳, time.time() 的格式
    - `audience: list` 通知受众的 uid 列表，例如["001", "002", "005"]表示只有这些用户应该接收这个通知。为空则表示所有用户都接收。

    '''

    def __init__(self):
        self.nid = ""
        self.title = ""
        self.content = ""
        self.expired = 0.0
        self.audience = []

    def to_dict(self):
        return {
            "nid": self.nid,
            "title": self.title,
            "content": self.content,
            "expired": self.expired,
            "audience": self.audience
        }

    def from_dict(self, notice_dict):
        """
        从 dict 中解析一条 notice，内容覆盖当前 Notice 实例
        """
        import time
        import random
        import json
        self.nid = notice_dict.get("nid") or (str(time.time()) + "/" + str(random.randint(100, 999)))   # 缺省值由当前时间戳与随机字符串混合得出
        self.title = notice_dict.get("title") or ""
        self.content = notice_dict.get("content") or ""
        self.expired = float(notice_dict.get("expired") or time.time() + 60 * 60 * 6)   # 缺省为发送6小时后过期
        self.audience = json.loads(str(notice_dict.get("audience")) or "[]")
        return self

    def dumps(self):
        import json
        return json.dumps(self.to_dict())

    def loads(self, notice_json):
        """
        从 json 中解析一条 notice，内容覆盖当前 Notice 实例
        """
        import json
        notice_dict = json.loads(notice_json)
        self.from_dict(notice_dict)
        return self
    
    def is_expired(self):
        import time
        if time.time() >= self.expired:
            return True
        return False

    def is_empty(self):
        if self.title == self.content == "":
            return True
        return False

    def is_for_user(self, uid):
        # 把 uid 和 self.audience 中的值都换成 str 去比较。
        audiences = map(str, self.audience)
        if len(self.audience) > 0 and str(uid) not in audiences:
            return False
        return True
