import os.path
import json
import pymongo
from utility import drop_id

# TODO: playlist 中添加 musicItem of music_list 的格式化检测工具

dir_path = './playlists/'
index_name = 'index.json'

class PlaylistUtil (object):
    def __init__(self):
        # 数据库名
        self._DATABASE_NAME = "musharing"
        self._COLLECTION_NAME = "playlists"

        # 连接数据库
        self._client = pymongo.MongoClient(host='localhost', port=27017)
        self._db = self._client[self._DATABASE_NAME]
        self._collection = self._db[self._COLLECTION_NAME]

    def _next_id(self):
        count = self._collection.count_documents({})
        return str(count + 1)

    def add(self, title: str, description: str, image: str, music_list):
        assert isinstance(music_list, (list, tuple))

        for i in range(len(music_list)):
            m = Music.from_dict(music_list[i])
            music_list[i] = m.to_dict()

        data = {
            "id": self._next_id(),
            "title": title,
            "description": description,
            "image": image,
            "size": len(music_list),
            "music_list": music_list
        }
        self._collection.insert_one(data)

    def get_index(self):
        index = list(self._collection.find())
        drop_id(index)
        for i in range(len(index)):
            try:
                index[i].pop("music_list")
            except KeyError:
                pass
        return index

    def get_playlist(self, id):
        playlist = self._collection.find_one({"id": id})
        if playlist == None:
            return None
        drop_id(playlist)
        for i in range(len(playlist.get("music_list"))):
            m = Music.from_dict(playlist["music_list"][i])
            playlist["music_list"][i] = m.to_dict()
        return playlist

    def get_count_playlist(self):
        """
        获取当前播放列表总数
        """
        return self._collection.count_documents({})

class Music (object):
    def __init__(self, AlbumImageUrl, album, artist, duration: int, fileUrl, mid, name):
            self.AlbumImageUrl = AlbumImageUrl
            self.album = album
            self.artist = artist
            self.duration = duration
            self.fileUrl = fileUrl
            self.mid = mid
            self.name = name

    @classmethod
    def from_dict(cls, music_dict):
        m = cls(AlbumImageUrl=music_dict.get("AlbumImageUrl", ""),
                album=music_dict.get("album", ""),
                artist=music_dict.get("artist", ""),
                duration=int(music_dict.get("duration", 0) or 0),
                fileUrl=music_dict.get("fileUrl", ""),
                mid=music_dict.get("id", ""),
                name=music_dict.get("name", ""))
        return m
        
    def to_dict(self):
        return {
            "AlbumImageUrl": self.AlbumImageUrl,
            "album": self.album,
            "artist": self.artist,
            "duration": self.duration,
            "fileUrl": self.fileUrl,
            "id": self.mid,
            "name": self.name
        }
