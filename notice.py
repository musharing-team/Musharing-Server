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
        self.nid = notice_dict.get("nid") or ""
        self.title = notice_dict.get("title") or ""
        self.content = notice_dict.get("content") or ""
        self.expired = float(notice_dict.get("expired")) or 0
        self.audience = notice_dict.get("audience") or []
        return self

    def dumps(self):
        import json
        return json.dumps(self.to_dict())

    def loads(self, notice_json):
        import json
        notice_dict = json.loads(notice_json)
        self.from_dict(notice_dict)
        return self
    
    def is_expired(self):
        import time
        if time.time() >= self.expired:
            return True
        return False

    def is_for_user(self, uid):
        if len(self.audience) > 0 and uid not in self.audience:
            return False
        return True
