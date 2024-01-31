import pymongo
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from datetime import datetime
import configparser

# 讀取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 取得 MongoDB 的連接資訊
mongodb_host = config.get('MongoDB', 'host')
mongodb_port = int(config.get('MongoDB', 'port'))
mongodb_database = config.get('MongoDB', 'database')
mongodb_username = config.get('MongoDB', 'username')
mongodb_password = config.get('MongoDB', 'password')

mongodb_url = f"mongodb+srv://{mongodb_username}:{mongodb_password}@{mongodb_host}.9jolvas.mongodb.net/?retryWrites=true&w=majority"

# 創建一個新的client並連接MongoDB
client = MongoClient(mongodb_url)

# 確認是否成功連線
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# 取得所有植物的學名
def get_plants(species:str)-> list:

    with MongoClient(mongodb_url) as client:
        db = client.wwg
        plants = db.plants
        plant = plants.find_one({"scientific name": species}, {"_id":0})
    return plant

# 儲存使用者的使用紀錄(植物名稱、圖片網址、圖片上傳時間、user id)
def save_record(species: str, image_url: str, date: datetime, userid: str) -> str:
    # save predict record
    with MongoClient(mongodb_url) as client:
        db = client.wwg
        records = db.records
        record = {
            'species': species,
            'image_url': image_url,
            'date': date,
            'user_id': userid
        }
        records.insert_one(record)
        return "done"

# 圖片旋轉木馬選單歷史紀錄(限5筆筆數，依上傳圖片時間降冪排序)
def get_species_records(userid, species, skip):
    with MongoClient(mongodb_url) as client:
        db = client.wwg
        records = db.records
        cursor = records.find({"user_id": userid, "species": species}, {"_id": 0}).sort("date", -1).skip(skip).limit(5)
        result = [obj for obj in cursor]
        # print(result)
        return result

# 旋轉木馬選單歷史紀錄(限10筆筆數)
def get_user_records(userid, skip):
        db = client.wwg
        records = db.records
        cursor =records.aggregate([
                {"$match": {"user_id": userid}},
                {"$group": {"_id": "$species", "total" : {"$sum" : 1}}},
                {"$sort": {"total": -1}},
                {"$skip": skip},
                {"$limit": 10},
                {"$project":{"_id":1, "total": 0}}
                ])
        result = [obj for obj in cursor]
        return result

# 針對模型判斷植物的學名及是否為外來種
def get_distinct_plant(idx):
    with MongoClient(mongodb_url) as client:
        db = client.wwg
        plants = db.plants
        cursor = plants.find({}, {"scientific name": 1, "isinvasive": 1, "_id": 0}).sort([("scientific name", 1)]).skip(idx).limit(1)
        result = [obj for obj in cursor]
        return result[0]


