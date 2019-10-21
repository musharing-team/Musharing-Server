# 发送消息

已登陆且身处 Room 的用户在当前所在的 Room 中发送消息。

### 请求URL:

- `http://musharing.server/send`
  
### 请求方式:

- POST

### 请求参数:

|参数名|必选|类型|说明|
|----|---|----- | --- |
| from_uid | 是  | string | 发起请求的用户uid |
| msg | 是  | string | 消息(MsgJson) |

 ### 返回示例

```json
  {
    "response": {
      "success": "send"
    }
  }
```

 **返回参数说明** 

|参数名|类型|说明|
|-----|-----|-----|
| success | string | 发送成功 |

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
