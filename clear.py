'''
服务停止后执行，数据库清理
⚠️该脚本系直接对数据库进行操作，请谨慎执行，在数据库变更时必须及时修改该脚本！
用来清理用户数据库 login、group 信息，避免再次开启服务时的错误
'''

import pymongo

# 连接数据库
client = pymongo.MongoClient(host='localhost', port=27017)
db = client["musharing"]
collection = db["users"]

rg = collection.update_many({"uid": {"$ne": "."}}, {"$set": {"group": "None"}})
print("group -> None:\tMatched: {m}, Modified: {c}".format(m=rg.matched_count, c=rg.modified_count))

rl = collection.update_many({"uid": {"$ne": "."}}, {"$set": {"login": "False"}})
print("login -> False:\tMatched: {m}, Modified: {c}".format(m=rl.matched_count, c=rl.modified_count))
