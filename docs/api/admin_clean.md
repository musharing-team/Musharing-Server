# 重置用户、群组状态

管理员重置服务中用户登录、群组等相关状态。

### 请求URL:

- `http://musharing.server/clean`

### 请求方式:

- POST

### 请求参数:

| 参数名     | 必选 | 类型   | 说明         |
| ---------- | ---- | ------ | ------------ |
| admin_name | 是   | string | 管理员用户名 |
| password   | 是   | string | 管理员密码   |

 ### 返回示例

```json
  {
    "response": {
      "success": "clean"
    }
  }
```

 **返回参数说明** 

| 参数名  | 类型   | 说明     |
| ------- | ------ | -------- |
| success | string | 操作成功 |

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


