import unittest
from google.cloud import storage
from datetime import datetime
from gcloud import upload_blob_from_stream
from PIL import Image
from urllib.request import urlopen
import os
import asyncio
import io


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"wildgreen-411520-37d993c760f1.json"

# 單元測試用假資料
dummy_bucket_name = "green01"
dummy_userid = "U12345678"


class TestMethod(unittest.TestCase):
    # 在測試之前的前置作業 -> 上傳到google cloud storage的圖片網址、讀取測試用的圖片"./image.jpg"
    def setUp(self) -> None:
        self.dummy_destination_blob_name = f"record/{dummy_userid[:7]}/img_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        with open ("./image.jpg","rb") as f:
            self.test_img = f.read()


    # 在測試結束後的善後清理 -> 刪除google cloud storage bucket裡面的測試用blob
    def tearDown(self) -> None:
        storage_client = storage.Client()
        bucket = storage_client.bucket(dummy_bucket_name)
        blob = bucket.blob(self.dummy_destination_blob_name)
        blob.delete()

    # 測試gcloud.py的upload_blob_from_stream -> 圖片網址是否相符、下載其圖片與測試用的圖片"./image.jpg"是否相同
    def test_upload_blob_from_stream(self) -> None:
        img_url = asyncio.run(upload_blob_from_stream(self.test_img, self.dummy_destination_blob_name))
        self.assertEqual(img_url, f"https://storage.googleapis.com/green01/{self.dummy_destination_blob_name}", "img_url not matched")
        download_img = Image.open(urlopen(img_url))
        test_img = Image.open(io.BytesIO(self.test_img))
        self.assertEqual(download_img, test_img , "images are not the same.")

if __name__ == "__main__":
    unittest.main()
