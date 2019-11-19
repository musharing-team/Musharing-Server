# 退出登录

已登陆的用户退出登录。

### 请求URL:

- `http://musharing.server/logout`
  
### 请求方式:

- POST

### 请求参数:

|参数名|必选|类型|说明|
|----|---|----- | --- |
| from_uid | 是  | string | 发起请求的用户uid |

 ### 返回示例

```json
  {
    "response": {
      "success": "logout"
    }
  }
```

 **返回参数说明** 

|参数名|类型|说明|
|-----|-----|-----|
| success | string | 成功退出登录 |

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
| from_not_login | 发起用户未登录 |
| from_not_exist | 发起用户不存在 |
| unexpected | 未知错误 |
