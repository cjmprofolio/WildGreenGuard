import uvicorn

from linebot.v3 import (
    WebhookHandler,
    
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from fastapi import FastAPI, Request
import json
import requests
import configparser

app = FastAPI()
config = configparser.ConfigParser()
config.read('config.ini')
configuration = Configuration(access_token=config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
HEADER = {
    'Content-type': 'application/json',
    'Authorization': f'Bearer {config.get("line-bot", "channel_access_token")}'
}

# body = {
#     'size': {'width': 2500, 'height': 1686},    # 設定尺寸
#     'selected': 'true',                        # 預設是否顯示
#     'name': '中文圖文選單',                             # 選單名稱
#     'chatBarText': '查看圖文選單',                        # 選單在 LINE 顯示的標題
#     'areas':[                                  # 選單內容
#         {
#           'bounds': {'x': 0, 'y': 0, 'width': 812, 'height': 887},           # 選單位置與大小
#           'action': {'type': 'message', 'text':'外來種植物辨識'}  # 點擊後開啟地圖定位，傳送位置資訊
#         },
#         {
#           'bounds': {'x': 813, 'y': 0, 'width':822, 'height': 887},     # 選單位置與大小
#           'action': {'type': 'message', 'text':'歷史紀錄查詢'}               # 點擊後傳送文字
#         },
#         {
#           'bounds': {'x': 1635, 'y': 0, 'width':865, 'height': 887},     # 選單位置與大小
#           'action': {'type': 'message', 'text':'前往網頁'}               # 點擊後傳送文字
#         },
#         {
#           'bounds': {'x': 0, 'y': 888, 'width':812, 'height': 799},     # 選單位置與大小
#           'action': {'type': 'message', 'text':'開發人員'}               # 點擊後傳送文字
#         }
#         {
#           'bounds': {'x': 813, 'y': 888, 'width':822, 'height': 799},     # 選單位置與大小
#           'action': {'type': 'message', 'text':'常見問題'}               # 點擊後傳送文字
#         }
#         {
#           'bounds': {'x': 635, 'y': 888, 'width':865, 'height': 799},     # 選單位置與大小
#           'action': {'type': 'message', 'text':'切換中英文'}               # 點擊後傳送文字
#         }
#     ]
#   }
# # 向指定網址發送 request
# req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
#                       headers=HEADER,data=json.dumps(body).encode('utf-8'))
# # 印出得到的結果
# print(req.text)
@app.get("/")
def getinfo():
    return "ok"

@app.post("/")
def call():
    return "post"

# @app.route("/", methods=['GET','POST'])
# def callback():
    # get X-Line-Signature header value
    # signature = request.headers['X-Line-Signature']

    # # get request body as text
    # body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # # handle webhook body
    # try:
    #     handler.handle(body, signature)
    # except InvalidSignatureError:
    #     app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
    #     abort(400)
#
    # return 'OK'

# @app.route("/", methods=['POST'])
# def linebot():
#     signature = request.headers['X-Line-Signature']
#     body = request.get_data(as_text=True)
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
#         abort(400)

#     return 'OK'

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port= 8000)