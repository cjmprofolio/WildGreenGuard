import unittest
from datetime import datetime
from pymongo import MongoClient
from db import get_plants, save_record, get_distinct_plant, get_all_records, get_species_records, get_user_records
import configparser

# 讀取配置文件
config = configparser.ConfigParser()
config.read("config.ini")

try:
    config.read("config.ini")
    host = config.get('MongoDB', 'host')
    port = config.get('MongoDB', 'port')
    # Continue with your MongoDB connection setup
except configparser.NoSectionError:
    print("Error: 'MongoDB' section not found in the configuration file.")

# 取得 MongoDB 的連接資訊
mongodb_host = config.get("MongoDB", "host")
mongodb_port = int(config.get("MongoDB", "port"))
mongodb_database = config.get("MongoDB", "database")
mongodb_username = config.get("MongoDB", "username")
mongodb_password = config.get("MongoDB", "password")

mongodb_url = f"mongodb+srv://{mongodb_username}:{mongodb_password}@{mongodb_host}.9jolvas.mongodb.net/?retryWrites=true&w=majority"


# 單元測試用假資料
dummy_plants =  {"scientific name": "a", "imgurl": "/path/to/a.jpg", "isinvasive": True}
dummy_records = {"species": 'a', "imgurl": "/path/to/user/a.jpg", "isinvasive" : True, "datetime": datetime.now()}
dummy_userid = "Utest"

# 單元測試
class TestMethods(unittest.TestCase):
    # 在測試之前的前置作業 -> 在plants collection建立dummy_plants
    @classmethod
    def setUpClass(cls) -> None:
        with MongoClient(mongodb_url) as client:
            db = client.wwg
            db.plants.insert_one(dummy_plants)

    # 在測試結束後的善後清理 ->  刪除假資料: scientific name "a", dummy_userid
    @classmethod
    def tearDownClass(cls) -> None:
        with MongoClient(mongodb_url) as client:
            db = client.wwg
            db.plants.delete_one({"scientific name": "a"})
            db.users.delete_one({"userid":dummy_userid})

    # 測試db.py的get_plants -> scientific name是否為a, isinvasive是否為 True
    def test_name(self) -> None:
        plant = get_plants("a")
        self.assertEqual(plant["scientific name"], "a", "scientific names not equaled")
        self.assertTrue(plant["isinvasive"], "isinvasive is not True")

    # 測試db.py的save_record -> 用dummy_userid建立的record裡，其imgurl是否為"/path/to/user/a.jpg"
    def test_save(self) -> None:
        save_record(dummy_records["species"], dummy_records["imgurl"], dummy_records["datetime"], dummy_userid, dummy_records["isinvasive"])
        with MongoClient(mongodb_url) as client:
            db = client.wwg
            user = db.users.find_one({"userid": dummy_userid})
            record = user["records"][0]
            self.assertEqual(record["imgurl"], "/path/to/user/a.jpg", "there is no record")
    
    # 測試db.py的get_distinct_plant -> 排序第15個的資料，scientific name是否為a, isinvasive是否為 True
    def test_distinct_plant(self) -> None:
        idx = 14
        plant = get_distinct_plant(idx)
        self.assertEqual(plant["scientific name"], "a", "scientific names not equaled")
        self.assertTrue(plant["isinvasive"], "isinvasive is not True")


if __name__ == "__main__":
    unittest.main()