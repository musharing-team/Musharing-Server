import functools

from utility import singleton
from user_util import UserUtil, RequestError
from rooms import Rooms

class AuthenticateUtil (object):
    def __init__(self, obj_user_util: UserUtil, rooms: Rooms):
        self._uu = obj_user_util
        self._rooms = rooms
        self.byUid = AuthenticateByUid(obj_user_util, rooms)
        self.byName = AuthenticateByName(obj_user_util, rooms)


class Authenticate (object):
    def __init__(self, obj_user_util: UserUtil, rooms: Rooms):
        self._uu = obj_user_util
        self._rooms = rooms

    def _user_exist(self, user, method=None):
        # method = self._uu.query_by_uid
        try:
            method(user)
            return True
        except RequestError:
            return False

    def _user_logined(self, user, method=None):
        if self._user_exist(user, method):
            if method(user).get("login") == str(True):
                return True
        return False

    def _user_in_room(self, user, method=None):
        if self._user_logined(user, method):
            if method(user).get("group") != str(None):
                return True
        return False


class AuthenticateByUid (Authenticate):
    def __init__(self, obj_user_util, rooms):
        super().__init__(obj_user_util, rooms)
        self.exist = functools.partial(self._user_exist, method=self._uu.query_by_uid)
        self.logined = functools.partial(self._user_logined, method=self._uu.query_by_uid)
        self.inroom = functools.partial(self._user_in_room, method=self._uu.query_by_uid)


class AuthenticateByName (Authenticate):
    def __init__(self, obj_user_util, rooms):
        super().__init__(obj_user_util, rooms)
        self.exist = functools.partial(self._user_exist, method=self._uu.query_by_name)
        self.logined = functools.partial(self._user_logined, method=self._uu.query_by_name)
        self.inroom = functools.partial(self._user_in_room, method=self._uu.query_by_name)
