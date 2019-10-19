import os.path
import json
import pymongo
from utility import drop_id

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
        return playlist
