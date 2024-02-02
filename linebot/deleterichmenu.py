import requests
import configparser

# 帶入config.ini檔案裏面的資訊
config = configparser.ConfigParser()
config.read('config.ini')

#查詢別名
url="https://api.line.me/v2/bot/richmenu/alias/list"
headers= {
    # 'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}
req = requests.get(url=url, headers=headers)
data = req.json()

# 找出RichMenuAliasId
richMenuAliasIds = []
for alias in data['aliases']:
    richMenuAliasIds.append(alias['richMenuAliasId'])

print(richMenuAliasIds)

#輸入要刪RichMenuAliasId
# li =["japanese",
#      "english",
#      "chinese"
#      ]

# 刪除RichMenuAliasId
for richMenuAliasId in richMenuAliasIds :
    url= f"https://api.line.me/v2/bot/richmenu/alias/{richMenuAliasId}" #不可動
    # headers = {"Authorization":"Bearer R/qZkeLXVhWeQTRq47q0OHABUeMjQOscOnLKpFEXSvwuqrYt2f9wl6F8X665PGX/yIERu8hkrHz0zihp17LurHosqIlrdZfobz3+zi9rvRx0oFM/V78dXYOvdlBt4bHh0mrzWXu3fgG+kb4otToXiQdB04t89/1O/w1cDnyilFU="}
    req = requests.delete(url=url, headers=headers)
    print(req.status_code)

#查詢richmenuId
url="https://api.line.me/v2/bot/richmenu/list"
req = requests.get(url=url, headers=headers)
data = req.json()

richMenuIds = []
for richMenuId in data["richmenus"]:
    richMenuIds.append(richMenuId["richMenuId"])

print(richMenuIds)

#輸入要刪除的richmenuid
# li = {"richmenu-12625ad602dcc176f639df35c2c3f5f0",
#       "richmenu-754c1759de73a212102633c0d8cf53b7",
#       "richmenu-e355ad76bb1a8ca1a2008f966fc147ca"
# }

# 刪除richmenuid
for richMenuId in richMenuIds:
    url= f"https://api.line.me/v2/bot/richmenu/{richMenuId}" #不可動
    # headers = {"Authorization":"Bearer R/qZkeLXVhWeQTRq47q0OHABUeMjQOscOnLKpFEXSvwuqrYt2f9wl6F8X665PGX/yIERu8hkrHz0zihp17LurHosqIlrdZfobz3+zi9rvRx0oFM/V78dXYOvdlBt4bHh0mrzWXu3fgG+kb4otToXiQdB04t89/1O/w1cDnyilFU="}
    req = requests.delete(url=url, headers=headers)
    print(req.status_code)

