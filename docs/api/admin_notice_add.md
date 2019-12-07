# 管理员发送通知

管理员发送通知。

### 请求URL:

- `http://musharing.server/admin/notice/add`

### 请求方式:

- POST

### 请求参数:

| 参数名     | 必选 | 类型          | 说明                                                         |
| ---------- | ---- | ------------- | ------------------------------------------------------------ |
| admin_name | 是   | string        | 管理员用户名                                                 |
| password   | 是   | string        | 管理员密码                                                   |
| nid        | 否   | string        | 通知的 id 识别码。若指定，请确保唯一性，推荐使用时间戳。（缺省值由当前时间戳与随机字符串混合得出） |
| title      | 是   | string        | 通知标题                                                     |
| content    | 是   | string        | 通知的具体内容                                               |
| expired    | 否   | float         | 通知过期的时间戳，python的 `time.time()` 格式；缺省为发送6小时后过期。 |
| audience   | 否   | json of alist | 通知受众的 uid 列表，例如["001", "002", "005"]表示只有这些用户应该接收这个通知。为空列表或缺省则表示所有用户都接收。 |

 ### 返回示例

```json
{
    "response": {
        "success": "notice"
    }
}
```

**返回参数说明** 

| 参数名  | 类型   | 说明     |
| ------- | ------ | -------- |
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

| 错误          | 说明                  |
| ------------- | --------------------- |
| not_permitted | 管理员用户名/密码错误 |
| unexpected    | 未知错误              |