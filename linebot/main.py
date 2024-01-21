import uvicorn

from fastapi import FastAPI, Request
import json
import requests
import configparser
import aiohttp
from db import save_record, get_records, get_distinct_record
from datetime import datetime
from PIL import Image
import io
from identifier import identifier
import time


app = FastAPI()
config = configparser.ConfigParser()
config.read('config.ini')

headers= {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}

trans_dict_repo = {}
trans_dict = {}
timer = -1

@app.get("/")
def getinfo():
    return "ok"

@app.post("/")
async def index(request: Request):

    # 預設語言為中文
    global trans_dict
    if not trans_dict:
        await get_trans_dict("chi")

    body = await request.json()
    print(body)
    events = body["events"]
    if len(events) == 0:
        return "ok"
    
    if "replyToken" in events[0]:
        replyToken = events[0]["replyToken"]
        payload={
            "replyToken" : replyToken,
            "messages" :[]
        }

        if events[0]["type"] == "postback":
            data = events[0]["postback"]["data"]

            if data == "外來種植物辨識":
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
            
            elif data == "歷史紀錄查詢":
                unique_record = await get_unique_record()
                if unique_record:
                    payload["messages"]= [await getHistory()]
                # if (裡面mongodb有資料，下列是您最近拍攝圖片的植物種類，用quick reply詢問是否查看更前面的歷史紀錄(前20筆不分種類)+旋轉木馬選單):
                # elif data =="test":
                #     pass
                # else: #顯示歷史紀錄
                #     data = json.loads(data)
                #     payload["messages"].append(await display_history(data))
                #     await replyMessage()
                await replyMessage(payload)
                # else (沒有資料):               
            else:
                payload["messages"].append(
                    {
                        "type": "postback",
                        "text": "no-data"
                    }
                    )
            await replyMessage(payload)
        elif events[0]["type"] == "message":
             if events[0]["message"]["type"] == "image":
                
                dump = json.dumps(events[0], indent=4)
                # print(dump)
                # 取得 userid
                user_id = events[0]["source"]["userId"]
                print(user_id)
                # 取得圖片
                img_id = events[0]["message"]["id"]
                print(img_id)
                img = await get_upload_image(img_id, payload)
                #避免使用者傳多張圖片
                if not isinstance(img, Image.Image):
                    payload["messages"].append({
                        "type": "text",
                        "text": trans_dict["oneimg"] #"唉呀，只能傳一張植物照片，不可以貪心哦！" 
                    })
                    await replyMessage(payload)

                else:
                    # predict plant species
                    species, isinvasive = identifier(img)
                    # species = "other" #測試retry_confirm
                    # isinvasive = "False" #測試retry_confirm
                    print(species, isinvasive)
                    # if species in plants -> save
                    # if species != "other":
                    #     # save record
                        # save image to gcp storage
                        # save_record(species, url, datetime.now(), user_id)
                    #     payload["messages"].append(await identifySucess(species))
                    #     await replyMessage(payload)
                    # else:
                    #     payload["messages"].append()
                    #     await replyMessage(payload)
                    #     await retry_confirm()

                    #  print(events[0])

    return "ok"        

#回覆訊息
async def replyMessage(payload: dict) -> str:
    url = "https://api.line.me/v2/bot/message/reply"
    async with aiohttp.ClientSession() as session:
        res = await session.post(url=url, headers=headers, json=payload)
        print(res.status)
    return "ok"

#將translate.json裡的內容載入到全域變數 trans_dict_repo
async def set_language_repo():
    global trans_dict_repo
    with open("translate.json","r", encoding="utf-8") as f :
        text_open = f.read()
        trans_dict_repo = dict(json.loads(text_open))
    # print(type(trans_dict_repo))
    # print(trans_dict_repo)
    return "done"

#根據指定的語言模式，從全域變數 trans_dict_repo 中提取相應的語言詞彙
async def get_trans_dict(mode:str):
    lan_int = {"chi": 0, "en": 1, "jp": 2}
    
    global trans_dict_repo
    if not trans_dict_repo:
        await set_language_repo()

    # key : [中文1, 英文2, 日文3]
    global trans_dict
    trans_dict = {key : value[lan_int[mode]] for key, value in trans_dict_repo.items()}
    # print(type(trans_dict))
    # print(trans_dict)
    # Assuming mode is the language you want to extract, e.g., "Chinese"
    # for english, translations in trans_dict.items():
    #     if mode in translations:
    #         language_translations[english] = translations[mode]

    return "ok"

#取得使用者上傳的圖片，並限制使用者上傳圖片的時間間隔需大於3秒
async def get_upload_image(img_id, payload):
    global timer
    if not timer:
        timer = time.time()
    delay = time.time() - timer
    # print(timer, delay)
    timer = time.time()
    if delay > 3:
        url=f"https://api-data.line.me/v2/bot/message/{img_id}/content"
        headers = {"Authorization":f"Bearer {config.get('line-bot', 'channel_access_token')}"}
        # post跟get都要寫下面那一行程式碼
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                stream = response.content
                st = await stream.read()
                img = Image.open(io.BytesIO(st))
                # img.show()
        # print("return image")
        # print(type(img))
        return img
    else:
        # # print("one image")
        return -1


# async def save_predict_record(name:str, url:str, date:datetime, user_id:str)-> None:
    
#     return

#辨識圖片成功的回覆訊息
# async def identifySucess(species):
#     msg = {
#         "type":"message",
#         "text":f"太棒了！你用得很得心應手嘛！這就是{species}。\n如果還有其他好玩的植物，也別忘了和我分享哦！"
#     }
#     return msg

# retry
async def retry_confirm():
    # action : postback data: 外來種植物辨識
    msg = {
                "type": "text",
                "text": trans_dict["idagain"], #"是否再次辨識植物"
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "action": {
                                        "type": "postback",
                                        "label": trans_dict["y"], #"是"
                                        "data":"外來種植物辨識"
                                    }
                        },
                        {
                            "type": "action",
                            "action": {
                                        "type": "postback",
                                        "label": trans_dict["n"], #"否"
                                        "data":"no-data"
                                    }
                        }
                    ]
                }
            }
    return msg    

async def get_all_records():
    # get_records()
    pass

async def get_unique_record():
    # get_distinct_record()
    pass

#外來種植物辨識功能
async def upload_image():
      msg = {
                "type": "text",
                "text": trans_dict["upaimg"], #"請上傳一張植物圖片"
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "imageUrl":"https://storage.googleapis.com/green01/identify/1.png",
                            "action": {
                                        "type": "cameraRoll",
                                        "label": trans_dict["upimg"] #"上傳圖片"
                                    }
                        },
                        {
                            "type": "action",
                            "imageUrl":"https://storage.googleapis.com/green01/identify/2.png",
                            "action": {
                                        "type": "camera",
                                        "label": trans_dict["camera"] #"開啟相機"
                                    }
                        }
                    ]
                }
            }
      return msg    

#歷史紀錄查詢功能
async def getHistory():
        msg = {
            "type": "template",
            "altText": "歷史紀錄查詢",
            "template": {
                "type": "image_carousel",
                "columns":[],
                "imageAspectRatio": "square",
                "imageSize": "cover"
            }
        }
            # carousel 5 records -> quick reply -> carousel next 5 records
        
            # unique_record: 學名, image_url
        # for record in unique_record:
        #     data = {"start": 0, "amount": 5}
        #     column = {
        #         "ImageUrl": record["image_url"],
        #         "action":
        #         {
        #             "type": "postback",
        #             "label": trans_dict[record["scientific_name"]],
        #             "data": json.dumps(data)
        #         }
        #     }
        #     msg["columns"].append(column)

        return msg

        # images = [
        #      {
        #             "thumbnailImageUrl": "https://storage.googleapis.com/wildgreenguard/%E7%B4%AB.jpg",
        #             "imageBackgroundColor": "#FFFFFF",
        #             "title": "紫花藿香薊",
        #             "text": "學名 Ageratum houstonianum",
        #             "actions": [
        #                 {
        #                     "type": "postback",
        #                     "label": "顯示最新上傳的圖片",
        #                     "data": "歷史紀錄查詢"
        #                 },
        #             ]
        #         },
        #         {
        #             "thumbnailImageUrl": "https://storage.googleapis.com/wildgreenguard/%E9%A6%AC%E7%BA%93%E4%B8%B9.jpg",
        #             "imageBackgroundColor": "#000000",
        #             "title": "馬纓丹",
        #             "text": "學名 Lantana camara",
        #             "actions": [
        #                 {
        #                     "type": "postback",
        #                     "label": "顯示上傳的最新圖片",
        #                     "data": "歷史紀錄查詢"
        #                 },
        #             ]
        #         },            
        # ]

        # columns = []

        # for image in images:
        #      columns.append({
        #           "thumbnailImageUrl": image["thumbnailImageUrl"],
        #           "imageBackgroundColor": image["imageBackgroundColor"],
        #           "title": image["title"],
        #           "text": image["text"],
        #           "actions": image["actions"]
        #      })

async def display_history(data:dict):
    msg = {
            "type": "template",
            "altText": "歷史紀錄查詢",
            "template": {
                "type": "carousel",
                "columns": []
            }
    }
    records = get_records(data)
    for record in records:
        column ={
            "thumbnailImageUrl": record["image_url"],
            "imageBackgroundColor": "#FFFFFF",
            "title": trans_dict[record["scientific_name"]],
            "text": record["scientific_name"],
            "actions": [
                {
                    "type": "postback",
                    "label": "",
                    "data": "歷史紀錄查詢"
                },
            ]
        }
        msg["columns"].append(column)
    
    return msg


#取得圖文選單id
async def getRichmenuId():
    url = "https://api.line.me/v2/bot/richmenu/{richMenuId}"
    headers = {"Authorization":f"Bearer {config.get('line-bot', 'channel_access_token')}"}
    req = requests.get(url=url,headers=headers)



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port= 8000)