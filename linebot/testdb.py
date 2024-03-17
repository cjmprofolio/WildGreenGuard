import unittest
from datetime import datetime
from pymongo import MongoClient
from db import get_plants, save_record
import configparser

# 讀取配置文件
config = configparser.ConfigParser()
config.read("config.ini")

# 取得 MongoDB 的連接資訊
mongodb_host = config.get("MongoDB", "host")
mongodb_port = int(config.get("MongoDB", "port"))
mongodb_database = config.get("MongoDB", "database")
mongodb_username = config.get("MongoDB", "username")
mongodb_password = config.get("MongoDB", "password")

mongodb_url = f"mongodb+srv://{mongodb_username}:{mongodb_password}@{mongodb_host}.9jolvas.mongodb.net/?retryWrites=true&w=majority"

dummy_plants =  {'scientific name': 'a', 'imgurl': '/path/to/a.jpg', 'isinvasive': True}
dummy_records = {"species": 'a', "imgurl": '/path/to/user/a.jpg', "isinvasive" : True, "datetime": datetime.now()}
dummy_userid = "Utest"

class TestMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with MongoClient(mongodb_url) as client:
            db = client.wwg
            db.plants.insert_one(dummy_plants)
        
    @classmethod
    def tearDownClass(cls) -> None:
        with MongoClient(mongodb_url) as client:
            db = client.wwg
            db.plants.delete_one({"scientific name": "a"})
            db.users.delete_one({"userid":dummy_userid})

    def test_name(self):
        plant = get_plants("a")
        self.assertEqual(plant["scientific name"], "a", "scientific names not equaled")
        self.assertTrue(plant["isinvasive"], "isinvasive is not True")

    def test_save(self):
        save_record(dummy_records["species"], dummy_records["imgurl"], dummy_records["datetime"], dummy_userid, dummy_records["isinvasive"])
        with MongoClient(mongodb_url) as client:
            db = client.wwg
            user = db.users.find_one({"userid": dummy_userid})
            record = user["records"][0]
            self.assertEqual(record["imgurl"], "/path/to/user/a.jpg", "there is no record")


if __name__ == "__main__":
    unittest.main()