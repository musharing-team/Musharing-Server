# 查询成员列表

已登陆且身处 Room 的用户请求当前所在的 Room 中的成员列表。

### 请求URL:

- `http://musharing.server/members`
  
### 请求方式:

- POST

### 请求参数:

|参数名|必选|类型|说明|
|----|---|----- | --- |
| from_uid | 是  |string | 发起请求的用户uid |

 ### 返回示例

```json
  {
    "response": {
      "members": [
          {"uid": "100", "name": "foo", "img": "http://a.com/foo.png"},
          {"uid": "101", "name": "bar", "img": "http://a.com/bar.png"}
      ]
    }
  }
```

 **返回参数说明** 

|参数名|类型|说明|
|-----|-----|-----|
| members | list | Room中用户列表(UserJson 组成的 list) |

 **错误** 

错误返回示例：

```json
  {
    "error": {
        "error": "unexpected"
    }
  }
```

错误说明：

| 错误 | 说明 |
| -- | -- |
| from_not_in_room | 发起用户没有处于任何 Room |
| from_not_login | 发起用户未登录 |
| from_not_exist | 发起用户不存在 |
| unexpected | 未知错误 |
