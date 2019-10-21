# 获取播放列表

已登陆且身处 Room 的用户获取一张在播放列表目录中的播放列表。

### 请求URL:

- `http://musharing.server/playlist`
  
### 请求方式:

- POST

### 请求参数:

|参数名|必选|类型|说明|
|----|---|----- | --- |
| from_uid | 是  | string | 发起请求的用户uid |
| playlist_id | 是 | string | 播放列表的id |

 ### 返回示例

```json
  {
    "response": {
        "id": "0",
        "title": "test",
        "size": 2,
        "music_list": [
            {
                "AlbumImageUrl": "http://a.com/Life.png",
                "album": "Life",
                "artist": "BaSO4",
                "duration": 0,
                "fileUrl": "http://a.com/file/潮湿.m4a",
                "id": "BaSO4_Life_06",
                "name": "潮湿"
            },
            {
                "AlbumImageUrl": "http://a.com/Life.png",
                "album": "Life",
                "artist": "BaSO4",
                "duration": 0,
                "fileUrl": "http://a.com/file/逆风.m4a",
                "id": "BaSO4_Life_07",
                "name": "逆风"
            }
        ]
    }
  }
```

 **返回参数说明** 

|参数名|类型|说明|
|-----|-----|-----|
| id | string | 播放列表id |
| title | string | 列表标题 |
| size | int | 播放列表中包含的曲目数 |
| music_list | list | 播放列表中的曲目(MusicJson 组成的 list)) |

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
| playlist_not_exist | 请求获取的播放列表不存在 |
| from_not_in_room | 发起用户没有处于任何 Room |
| from_not_login | 发起用户未登录 |
| from_not_exist | 发起用户不存在 |
| unexpected | 未知错误 |
