# 添加成员

已登陆且身处 Room 的用户拉取某个已登陆且为加入 Room 的用户加进自己当前所在的 Room。

### 请求URL:

- `http://musharing.server/attend`
  
### 请求方式:

- POST

### 请求参数:

|参数名|必选|类型|说明|
|----|---|----- | --- |
| from_uid | 是  |string | 发起请求的用户uid |
| target_name | 是  |string | 欲加的目标用户name |

 ### 返回示例

```json
  {
    "response": {
      "success": "attend"
    }
  }
```

 **返回参数说明** 

|参数名|类型|说明|
|-----|-----|-----|
| success | string | 请求成功，已添加 |

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
| target_in_room | 目标用户已经加入了某个 Room |
| target_not_login | 目标用户没有登录 |
| target_not_exist | 目标用户不存在 |
| from_not_login | 发起用户未登录 |
| from_not_exist | 发起用户不存在 |
| unexpected | 未知错误 |
