'''
获取符合通用接口的json

用 flask.jsonify 可以让响应的 headers 里的 Content—Type 变成 application/json，而用 json.dumps 返回 json 字符串的话类型会是 text/html。
'''

import json
from flask import jsonify
from user import User

debug = True

def response_unexpected(e=None):
    '''
    返回意外错误
    '''
    content = {"error": "unexpected"}
    if debug:
        content["debug"] = str(e)
    res = {"error": content}
    # return json.dumps(res)
    return jsonify(res)

def response_success(content=None):
    '''
    返回成功请求的结果
    '''
    try:
        assert isinstance(content, dict)
        res = {"response": content}
        # return json.dumps(res)
        return jsonify(res)
    except Exception as e:
        return response_unexpected(e)

def response_error(content=None, e=None):
    '''
    返回错误
    '''
    try:
        assert isinstance(content, dict)
        if debug:
            content["debug"] = str(e)
        res = {"error": content}
        # return json.dumps(res)
        return jsonify(res)
    except Exception as ex:
        return response_unexpected(ex)

def get_simple_success_content(content: str):
    '''
    简单的成功response

    用于：添加Room成员/发送消息/离开Room/退出登录
    ```json
    {"success": "..."}
    ```
    '''
    return {
        "success": content
    }

def get_simple_error_content(content: str):
    '''
    简单的 Error response

    用于：返回各种错误
    ```json
    {"error": "..."}
    ```
    '''
    return {
        "error": content
    }

def get_single_user_content(user: User):
    '''
    获取单个用户的response

    >用于：登录/注册

    ```json
    {"uid": "...", "name": "...", "img": "..."}
    ```
    '''
    return {
        "uid": user.uid,
        "name": user.name,
        "img": user.img
    }

class ResponseError:
    """
    可能需要返回的各种错误的错误代码，整理在这里，防止 typo 导致返回不一致
    """
    unexpected = "unexpected"

    from_not_exist = "from_not_exist"
    from_not_login = "from_not_login"
    from_not_in_room = "from_not_in_room"

    target_not_exist = "target_not_exist"
    target_not_login = "target_not_login"
    target_in_room = "target_in_room"
    
    fail_to_get_index = "fail_to_get_index"

    playlist_not_exist = "playlist_not_exist"

    name_occupied = "name_occupied"

    wrong_name = "wrong_name"
    wrong_password = "wrong_password"

    not_permitted = "not_permitted"
