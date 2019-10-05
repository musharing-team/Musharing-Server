import os.path
import json

dir_path = './playlists/'
index_name = 'index.json'

def get_index():
    file_path = dir_path + index_name
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = json.load(f)
            return content
        return None
        

def get_playlist(id):
    file_path = dir_path + id + '.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = json.load(f)
            return content
    return None