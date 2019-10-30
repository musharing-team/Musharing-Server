# 注册

用户注册接口。

### 请求URL:

- `http://musharing.server/register`
  
### 请求方式:

- POST

### 请求参数:

|参数名|必选|类型|说明|
|----|---|----- |--- |
| name |是  |string | 用户名(Base64编码)   |
| password |是  |string | 密码(hmac加密)    |
| img     |是  |string | 头像图片URL    |

 ### 返回示例

```json
  {
    "response": {
      "uid": "100",
      "name": "foo",
      "img": "http://example.com/img/foo.png"
    }
  }
```

 **返回参数说明** 

|参数名|类型|说明|
|-----|-----|-----|
|uid | string | 用户识别id |
|name |string |用户名(Base64)   |
|img   |string | 头像图片URL    |

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
| name_occupied | 用户名被占用 |
| unexpected | 未知错误 |
