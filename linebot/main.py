import uvicorn
from fastapi import FastAPI, Request
import json
import requests
import configparser
import aiohttp
from db import save_record,get_user_records, get_species_records, get_plants
from datetime import datetime
from PIL import Image
import io
from identifier import identifier
import time
from gcloud import upload_blob_from_stream
import asyncio

# FastAPI
app = FastAPI()

# 帶入config.ini檔案裏面的資訊
config = configparser.ConfigParser()
config.read('config.ini')

# 標頭
headers= {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}

# 讀取translate.json裡面的內容轉換為字典形式(初始為空字典)
trans_dict_repo = {}
# translate.json裡面的翻譯內容(初始為空字典)
trans_dict = {}
# 圖片張數(初始為空列表)
# img_queue = []
# 計時器初始值為-1
# timer = -1

# Fast API 讀取
@app.get("/")
def getinfo():
    return "ok"

# Fast API 發送
@app.post("/")
async def index(request: Request):
    # 從請求(request)中讀取JSON格式的內容
    body = await request.json()
    print(body)
    # 從JSON內容中提取名為"events"的鍵對應的值
    events = body["events"]

    # 連線webhook偵測用
    if len(events) == 0:
        return "ok"

    # 取得userid
    userid = events[0]["source"]["userId"]
    # 預設語言為中文
    global trans_dict
    if not trans_dict:
        await get_trans_dict("chi", userid=userid)
    
    # 回覆訊息，訊息內容預設為空列表
    if "replyToken" in events[0]:
        replyToken = events[0]["replyToken"]
        payload={
            "replyToken" : replyToken,
            "messages" :[]
        }
        # 型別為postback，取出postback裡面的data
        if events[0]["type"] == "postback":
            data = events[0]["postback"]["data"]
            # 外來種植物辨識功能-上傳一張植物圖片，附有上傳圖片及開啟相機的功能
            if data == trans_dict["idplant"]:
                payload["messages"].append(await upload_image())
            # 根據圖文選單所選擇的語言，以相應的語言回覆訊息
            elif data in ["richmenu-changed-to-chinese", "richmenu-changed-to-english", "richmenu-changed-to-japanese"]:
                match data:
                    case "richmenu-changed-to-chinese":
                        await get_trans_dict("chi")
                    case "richmenu-changed-to-english":
                        await get_trans_dict("en")
                    case "richmenu-changed-to-japanese":
                        await get_trans_dict("jp")
                return "change language done"
            # 歷史紀錄查詢回覆內容:好好欣賞植物圖片吧!
            elif data == trans_dict["enjimg"]:
                payload["messages"].append(await view_image_info())
            # 歷史紀錄查詢點選圖片旋轉木馬選單後出現使用者拍攝的圖片
            elif data[8:15] == "storage":
                payload["messages"]= [await share_img(data)]
            # 歷史紀錄查詢回覆內容:點選上方的「查看更多資訊」吧!
            elif data == trans_dict["clvimgin"]:
                payload["messages"].append(await click_view_info())
            # 歷史紀錄查詢功能的data
            else: 
                data = json.loads(data)
                action = data["action"]
                skip = data["skip"]
                # 旋轉木馬選單歷史紀錄(Mongodb)
                if action == "search":
                    user_records = get_user_records(userid, skip)
                    # 歷史紀錄植物物種小於10種的回覆:目前歷史紀錄裡只有上面的植物種類喔！
                    if not user_records:
                        payload["messages"].append({
                            "type": "text",
                            "text" : trans_dict["curhis"] 
                    })
                    # 歷史紀錄查詢quick reply:是否再顯示其他的植物種類?
                    else:   
                        payload["messages"]= [
                            await get_history(user_records, data),
                            await quick_reply(text=trans_dict["disother"], actions=[
                                {"action_type":"postback", "label":trans_dict["y"], "data": json.dumps({"action": action, "skip": skip + 10})},
                                {"action_type":"postback", "label":trans_dict["n"], "data": trans_dict["clvimgin"]}])]
                # 圖片旋轉木馬選單歷史紀錄(Mongodb)
                else:
                    species = data["species"]
                    records = get_species_records(userid, species, skip)
                    # 沒有歷史紀錄的回覆:沒有任何歷史紀錄喔!
                    if not records:
                        payload["messages"].append({
                                "type": "text",
                                "text" : trans_dict["norec"]
                        })
                    # 不再查看先前的歷史紀錄回覆:好好欣賞植物圖片吧!
                    else:
                        payload["messages"]= [await display_history(records),
                                          await quick_reply(text=trans_dict["prehis"], actions=[
                            {"action_type":"postback", "label":trans_dict["y"], "data": json.dumps({"action": action, "species": species, "skip": skip + 5})},
                            {"action_type":"postback", "label":trans_dict["n"], "data": trans_dict["enjimg"]}])]
            await reply_message(payload)
        # 型別為message
        elif events[0]["type"] == "message":
             if events[0]["message"]["type"] == "image":

                # 取得圖片id
                img_id = events[0]["message"]["id"]
                print(img_id)
                
                # global img_queue
                # img_queue.append(img_id)
                img = await get_upload_image(img_id)
                # 避免使用者傳多張圖片
                # time.sleep(3)
                # await asyncio.sleep(3) 
                # if len(img_queue) > 1:
                #     img_queue = []
                #     payload["messages"].append({
                #         "type": "text",
                #         "text": trans_dict["oneimg"] #"唉呀，只能傳一張植物照片，不可以貪心哦！" 
                #     })
                #     await reply_message(payload)
                #     return "ok"
                # if not isinstance(img, Image.Image):
                #     payload["messages"].append({
                #         "type": "text",
                #         "text": trans_dict["oneimg"] #"唉呀，只能傳一張植物照片，不可以貪心哦！" 
                #     })
                #     await reply_message(payload)
                #     return "ok"
                # 導入模組辨別植物名稱跟是否為外來種(identifier.py)
                species, isinvasive = await identifier(img)
                # species = "other" #測試retry_confirm
                # isinvasive = "False" #測試retry_confirm
                print(species, isinvasive)
                # species = "other"
                # if species in plants -> save 如果是符合辨識的植物種類就儲存
                if species != "other":
                    # save record
                    # image -> upload img -> img url -> mongodb
                    # 儲存圖片到 GCP storage (gcloud.py)
                    img_url = await upload_blob_from_stream(img, f"record/{userid[:7]}/img_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                    save_record(species, img_url, datetime.now(), userid)
                    # 辨別植物成功的回覆訊息
                    payload["messages"].append(await identify_success(species, userid))
                   
                # 辨別植物失敗的回覆訊息
                else:
                    payload["messages"]=[
                        await identify_fail(),
                        await retry_confirm()
                    ]
                await reply_message(payload)
    return "ok"        

# 回覆訊息
async def reply_message(payload: dict) -> str:
    url = "https://api.line.me/v2/bot/message/reply"
    async with aiohttp.ClientSession() as session:
        res = await session.post(url=url, headers=headers, json=payload)
        print(res.status)
        print(await res.json())
        # print(res.text)
    return "ok"

# 將translate.json裡的內容載入到全域變數 trans_dict_repo
async def set_language_repo():
    global trans_dict_repo
    with open("translate.json","r", encoding="utf-8") as f :
        text_open = f.read()
        trans_dict_repo = dict(json.loads(text_open))
    return "done"

# 根據指定的語言模式，從全域變數 trans_dict_repo 中提取相應的語言詞彙
# **kwargs目前只用在userid
async def get_trans_dict(mode:str, **kwargs):
    # key : [中文0, 英文1, 日文2]
    lan_int = {"chi": 0, "en": 1, "jp": 2}
    lan_id = {"richmenu-6fd7dd62a7a00d50acb56565c9676eed": "chi", 
              "richmenu-b5f1a9d44f3642dc0bf8f210c1b93664": "en", 
              "richmenu-c2ab21f8873a2b671ed64bfe84581b4b": "jp"}

    global trans_dict_repo
    # 如果翻譯字典尚未被設定，則呼叫 set_language_repo() 函數進行設定
    if not trans_dict_repo:
        await set_language_repo()
        userid = kwargs.get("userid")
        url = f"https://api.line.me/v2/bot/user/{userid}/richmenu"
        # 使用 aiohttp 客戶端建立連線，發送 GET 請求
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                res = await response.json()
                # 根據回傳的 richMenuId 取得對應的語言模式
                mode = lan_id[res["richMenuId"]]

    # key : [中文0, 英文1, 日文2]
    global trans_dict
    # 使用字典生成式建立 trans_dict 字典，選擇對應語言模式的翻譯
    trans_dict = {key : value[lan_int[mode]] for key, value in trans_dict_repo.items()}

    return "ok"

# 取得使用者上傳的圖片，並限制使用者上傳圖片的時間間隔需大於3秒
async def get_upload_image(img_id):
    # global timer
    # if not timer:
    #     timer = time.time()
    # delay = time.time() - timer
    # print(timer, delay)
    # timer = time.time()
    # if delay > 5:
        url=f"https://api-data.line.me/v2/bot/message/{img_id}/content"
    #     headers = {"Authorization":f"Bearer {config.get('line-bot', 'channel_access_token')}"}
    #     # post跟get都要寫下面那一行程式碼
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                stream = response.content
                st = await stream.read()
                img = Image.open(io.BytesIO(st))
    #             # img.show()
    #     # print("return image")
    #     # print(type(img))
        return img
    # else:
    #     # # print("one image")
    #     return -1
    # url=f"https://api-data.line.me/v2/bot/message/{img_id}/content"
    # # 使用 aiohttp 客戶端建立連線，發送 GET 請求
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(url=url, headers=headers) as response:
    #         stream = response.content
    #         st = await stream.read()
    #         img = Image.open(io.BytesIO(st))
            # img.show()
    # print("return image")
    # print(type(img))
    # return img

# 辨識圖片成功的回覆訊息(帶入用戶名跟植物名)
async def identify_success(species,userid):
    user_name = await get_user_name(userid)
    plant_name_with_spaces = f" {trans_dict[species]} "
    msg = {
        "type": "text",
        "text": trans_dict["idsuc"].replace("[人名]", user_name).replace("[植物名]", plant_name_with_spaces)
    }
    return msg

# 辨識圖片失敗的回覆訊息
async def identify_fail():
    msg = {
        "type": "text",
        "text": trans_dict["idfail"]
    }
    return msg

# quick reply:是否再次辨識植物
async def retry_confirm():
    return await quick_reply(trans_dict["idagain"], [{"action_type": "postback", "label": trans_dict["y"], "data": "外來種植物辨識"}, \
                            {"action_type": "postback", "label": trans_dict["n"], "data": trans_dict["thxuse"]}])

# quick reply
async def quick_reply(text, actions):
    quick_reply_items = []

    for action in actions:
        item = {
            "type": "action",
            "imageUrl": action.get("imageUrl"),
            "action": {
                "type": action["action_type"],
                "label": action["label"]
            }
        }
        try:
            item["imageUrl"] = action["imageUrl"]
        except:
            pass
        # Add additional parameters based on action type 依照action的型別新增額外的參數
        if action["action_type"] == "postback":
            item["action"]["data"] = action.get("data")

        quick_reply_items.append(item)

    msg = {
        "type": "text",
        "text": text,
        "quickReply": {
            "items": quick_reply_items
        }
    }

    return msg

# 外來種植物辨識功能-上傳一張植物圖片，附有上傳圖片及開啟相機的功能
async def upload_image():
    imageUrl_a = "https://storage.googleapis.com/green01/identify/1.png"
    imageUrl_b = "https://storage.googleapis.com/green01/identify/2.png"
    
    return await quick_reply(trans_dict["upaimg"], 
                             [{"imageUrl":imageUrl_a, "action_type":"cameraRoll", "label":trans_dict["upimg"]},
                            {"imageUrl":imageUrl_b, "action_type":"camera", "label":trans_dict["cameraon"]}])

# 旋轉木馬選單-歷史紀錄查詢功能(列出使用者辨識成功的植物種類)
async def get_history(user_records, data:dict):
    msg = {
            "type": "template",
            "altText": "歷史紀錄查詢(列出使用者辨識成功的植物種類)",
            "template": {
                "type": "carousel",
                "columns": []
            }
    }
    # carousel 10 records -> quick reply -> carousel other records
    # unique_record: 學名, image_url
    for record in user_records:
        plant = get_plants(record["_id"])
        name = plant['scientific name']
        data = {"species": name,"action": "showup", "skip": 0}

        column ={
            "thumbnailImageUrl": plant["imgurl"],
            "imageBackgroundColor": "#FFFFFF",
            "title": trans_dict[name],
            "text": name,
            "actions": [
                {
                    "type": "postback",
                    "label": trans_dict["vimgin"], #查看更多資訊
                    "data": json.dumps(data)
                },
            ]
        }
        msg["template"]["columns"].append(column)
    return msg
        

# 圖片旋轉木馬選單-歷史紀錄查詢功能(列出使用者辨識成功的植物圖片資訊)
async def display_history(records:dict):
    msg = {
            "type": "template",
            "altText": "歷史紀錄查詢(列出使用者辨識成功的植物圖片資訊)",
            "template": {
                "type": "image_carousel",
                "columns":[],
            }
        }
            # carousel 5 records -> quick reply -> carousel next 5 records
        
            # unique_record: 學名, image_url
    for record in records:            
            column = {
                "imageUrl": record["image_url"],
                "action": {
                    "type": "postback",
                    "label": trans_dict["dl"],
                    "data": record["image_url"]
                } 
            }
            msg["template"]["columns"].append(column)
    print(msg)
        
    return msg

# 歷史紀錄查詢點選圖片旋轉木馬選單後出現使用者拍攝的圖片
async def share_img(data:str):
    msg = {
        "type": "image",
        "originalContentUrl": data,
        "previewImageUrl": data
    }
    return msg
# 取得使用者名稱
async def get_user_name(userid: str):
    url = f"https://api.line.me/v2/bot/profile/{userid}"
    headers = {"Authorization":f"Bearer {config.get('line-bot', 'channel_access_token')}"}
    async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                res = await response.json()
                # print(res.status)
                # print(res.text)
                print(res)
                user_name = res["displayName"]
                # print(user_name)
            return user_name

# 是否再查看先前的歷史紀錄quick reply 按否的回覆: 好好欣賞現有的植物圖片吧!   
async def view_image_info():
    msg = {
            "type": "text",
            "text": trans_dict["enjimg"]
        }
    return msg

# 是否再顯示其他的植物種類quick reply 按否的回覆:點選上方的「查看更多資訊」吧!
async def click_view_info():
    msg = {
        "type": "text",
        "text": trans_dict["clvimgin"]
    }
    return msg   

# 取得圖文選單id
async def get_richmenu_id():
    url = "https://api.line.me/v2/bot/richmenu/{richMenuId}"
    headers = {"Authorization":f"Bearer {config.get('line-bot', 'channel_access_token')}"}
    req = requests.get(url=url,headers=headers)

# 點選圖片旋轉木馬選單後跳出圖片功能(供分享、下載)
# async def share_img():
#     msg = {
#     "type": "image",
#     "originalContentUrl": "https://example.com/original.jpg",
#     "previewImageUrl": "https://example.com/preview.jpg"
#     }
#     return msg

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port= 8000)