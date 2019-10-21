# 获取播放列表

已登陆且身处 Room 的用户获取一张播放列表目录。

### 请求URL:

- `http://musharing.server/category`
  
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
        "categories": [
            {"id": "100", "title": "Playlist_1", "description": "A test playlist.", "image": "https://a.com/a.png"},
            {"id": "101", "title": "Playlist_2", "description": "Another test playlist.", "image": "http://a.com/b.png"}
        ]
    }
  }
```

 **返回参数说明** 

|参数名|类型|说明|
|-----|-----|-----|
| categories | list | 播放列表(CategoryJson 组成的 list) |

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
| fail_to_get_index | 无法获取播放列表目录 |
| from_not_in_room | 发起用户没有处于任何 Room |
| from_not_login | 发起用户未登录 |
| from_not_exist | 发起用户不存在 |
| unexpected | 未知错误 |
