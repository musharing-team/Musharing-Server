# 接收消息

已登陆且身处 Room 的用户接收当前待接收的所有消息。

### 请求URL:

- `http://musharing.server/receive`
  
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
      "messages": [
          "MsgJson",
          "MsgJson"
      ]
    }
  }
```

 **返回参数说明** 

|参数名|类型|说明|
|-----|-----|-----|
| messages | list | 当前待接收的所有消息("MsgJson" 组成的 list)) |

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
