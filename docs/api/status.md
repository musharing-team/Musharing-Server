# 获取当前服务状态

管理员获取当前服务状态。

### 请求URL:

- `http://musharing.server/status`
### 请求方式:

- POST 

### 请求参数:

| 参数名   | 必选 | 类型   | 说明         |
| -------- | ---- | ------ | ------------ |
| name     | 是   | string | 管理员用户名 |
| password | 是   | string | 管理员密码   |

 ### 返回示例

```json
{
  "response": {
    "status": {
      "inroom_num": 1, 
      "login_num": 2, 
      "notice_num": 1, 
      "playlist_num": 2, 
      "rooms_num": 0, 
      "user_num": 10 
    }
  }
}
```

**返回参数说明** 

| 参数名 | 类型   | 说明     |
| ------ | ------ | -------- |
| status | object | 各种数据 |

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

| 错误          | 说明                  |
| ------------- | --------------------- |
| not_permitted | 管理员用户名/密码错误 |
| unexpected    | 未知错误              |