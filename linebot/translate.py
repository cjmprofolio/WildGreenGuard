import json

trans_dict = {
    # 物種
    "Ageratum houstonianum":["紫花藿香薊","Flossflower","ムラサキカッコウアザミ"],
    "Bidens pilosa var radiata":["大花咸豐草","Pilose Beggarticks","タチアワユキセンダングサ"],
    "Bryophyllum pinnatum":["落地生根","Life plant","セイロンベンケイ"],
    "Chloris barbata":["孟仁草","Swollen finger grass","クロリス・バルバタ"],
    "Conyza species":["加拿大蓬","Horseweed","ヒメムカシヨモギ"],
    "Crassocephalum crepidioides":["昭和草","Redflower ragleaf","ベニバナボロギク"],
    "Lantana camara":["馬纓丹","Common lantana","ランタナ"],
    "Leucaena leucocephala":["銀合歡","River tamarind","ギンネム"],
    "Mikania micrantha":["小花蔓澤蘭","Bitter vine","ツルヒヨドリ"],
    "Pennisetum purpureum":["象草","Napier grass","ナピアグラス"],
    "Rhynchelytrum repens":["紅毛草","Natal Grass","ルビーガヤ"],
    "Syngonium podophyllum":["合果芋","Arrowhead Plant","シンゴニウム・ポドフィラム"],
    "Tithonia diversifolia":["王爺葵","Tree marigold","ニトベギク"],
    "Eleusine indica":["牛筋草","Goosegrass","オヒシバ"],
    "Cynodon dactylon":["狗牙根","Bermuda Grass","ギョウギシバ"],
    "Miscanthus species":["芒草","Silver grass","ススキ"],
    "Amaranthus spinosus":["刺莧","Pilose Beggarticks","ハリビユ"],
    "Celosia argentea":["雞冠花","Silver cock's comb","セロシア"],
    "Cardiospermum halicacabum":["倒地鈴","Balloon vine","フウセンカズラ"],
    # Line bot圖文選單
    "qa":["常見問題","FAQ","FAQ"],
    "dev":["開發人員","Developers","開発者"],
    "web":["網頁","Website","Webサイト"],
    "idplant":["外來種植物辨識","Identify Invasive Plants","外来種植物を識別する"],
    "history":["歷史紀錄查詢","Search History","履歴を検索する"],
    # Line bot 外來種植物辨識對話
    "oneimg":["唉呀，只能傳一張植物照片，不可以貪心哦！","Oops, only one plant picture at a time.","アップできるのは一度に一枚の写真だけだよ。"],
    "upaimg":["請上傳一張植物圖片","Please upload a picture of the plant.","一枚の植物の画像をアップロードしてね"],
    "upimg":["上傳圖片","Upload a picture","画像をアップロード"],
    "cameraon":["開啟相機","Turn on the camera","カメラを開く"],
    "idsuc":["太棒了！[人名]\n你用得很得心應手嘛!\n這就是[植物名]。\n如果還有其他的植物，也別忘了和我分享哦！","Wow, [人名]\nYou nailed it!\nThis is [植物名].\nIf there are any other plants, please don’t hesitate to share them with me!","やったね！[人名]\nうまくいったよ！\nこれが[植物名]だよ。\n他にも面白い植物があれば、ぜひ教えてくれるとうれしいな！"],
    "idfail":["哎呀，辨識失敗了嗎？\n不要灰心，你可以試試換個角度拍攝，再傳給我圖片，我再幫你看看","Oh dear, the plant can't be found.\nCould you please take another photo and give it another try?","あらら、植物が見つからなかった。\nもう一度写真を取り直してみてくれる？"],
    "idagain":["是否再次辨識植物","Would you like to identify the plants again?","もう一度植物を識別する？"],
    "thxuse":["感謝你使用WildGreenGuard!\n如果還有其他的植物，別忘了和我分享哦！","Thank you for using WildGreenGuard.\nIf there are any other plants, please don’t hesitate to share them with me!","WildGreenGuardをご利用いただきありがとうございます。\n他にも面白い植物があれば、ぜひ教えてくれるとうれしいな！"],
    "y":["是","Yes","はい"],
    "n":["否","No","いいえ"],
    # Line bot 歷史紀錄查詢對話
    "norec":["沒有任何歷史紀錄喔!","No history records found!","履歴が見つからなかったよ!"],
    "species":["植物名稱","Plant name","植物名"],
    "sciname":["學名","Scientific name","学名"],
    "uptime":["圖片上傳時間","Time of picture upload","アップロードした時間"],
    "prehis":["是否再查看先前的歷史紀錄","Would you like to check the previous history?","もう一度過去の履歴を見る？"],
    "vimgin":["查看更多資訊","View more info","詳細を見る"],
    "enjimg":["好好欣賞植物圖片吧!","Enjoy the beauty of the uploaded plant images!","アップロードされた植物の画像の美しさをお楽しみくださいね！"],
    "clvimgin":["點選上方的「查看更多資訊」吧!","Click on 'View More Info' above!","上の「詳細を見る」をタップしてね！"],
    "disother":["是否再顯示其他的植物種類?","Would you like to see additional plant species?","他の植物種も表示するか？"],
    "curhis":["目前歷史紀錄裡只有上面的植物種類喔！","The current history record only contains plant species as above!","現在の履歴には上記の植物種のみが含まれている！"],
    "dl":["下載","Download","ダウンロード"],
    # 網頁
    "real":["即時影像植物辨識","Real-time Image-Based Plant Identification","リアルタイム画像識別"],
    "data":["植物資料庫","Plant Database","植物データベース"],
    "record":["植物辨識紀錄","Plant Identification records","植物識別履歴"],
    "dt":["資料","Data","データ"],
    "about":["關於","About","情報"],
    "cameraoff":["關閉相機","Turn off the camera","カメラを閉じる"],
    "selectf":["選擇圖片","Select the picture","画像を選択"],
    "confirm":["確認","Upload","完了"],
    # 常見問題
    "q1":["1. 介紹WildGreenGuard外來種植物圖片辨識。","1. Introduction to WildGreenGuard Invasive Plant Image Recognition","1. WildGreenGuard外来種植物画像判別の紹介してほしい。"],
    "a1":["Ans: 是一款以台灣入侵種為主題的外來種植物圖片辨識line機器人，\n含有中英日功能的辨識機器人，操作簡單、全家大小皆可使用。","Ans: It is a Line bot designed to identify invasive plant species in Taiwan.\nIt is equipped with image recognition capabilities and supports Chinese, English, and Japanese.","Ans: 台湾の外来種植物を判別するためのLineボットです。\n画像認識機能を備え、中国語、英語、日本語に対応しています。"],
    "q2":["2. 為什麼植物圖片辨識不成功?","2. Why is plant image recognition not successful?","2. どうして画像がうまく認識されない?"],
    "a2":["Ans: 上傳的植物圖片需在陽光充足的環境下拍攝，且畫面須清晰不模糊。\n也可上傳不同拍攝角度的植物圖片以利辨識。","Ans: The uploaded plant photos should be taken in well-lit conditions, and the images must be clear.\nUploading images from different angles would improve the success rate of recognition.","Ans: 画像が鮮明でない場合、正しい検索結果が表示されない場合があります。\n明るい環境での撮影と撮影する角度や位置を変更することをおすすめします。"],
    "q3":["3.我可以上傳其他不是外來種植物嗎?","3. Can I upload pictures of non-invasive plants?","3. 外来種以外の植物の画像を判別できますか？"],
    "a3":["Ans: WildGreenGuard是一款以台灣入侵種為主題的外來種植物圖片辨識line機器人，\n您上傳一般植物圖片可能無法滿足您的需求。","Ans: WildGreenGuard is a Line bot designed to identify invasive plant species in Taiwan.\nUploading pictures of common plants may not meet your needs.","Ans: WildGreenGuardは台湾の外来種植物しか判別できません。"],
    "q4":["4.圖片的歷史紀錄會保留多久?","4. How long will the history of uploaded images be retained?","4. 投稿した写真はいつまで保存されますか？"],
    "a4":["Ans: 歷史紀錄將會保留您一周內上傳的圖片。","Ans: The history of uploaded images will be retained for one week.","Ans: 最大で一週間まで保存されます。"],
    # 人名
    "ZJM":["張家銘","ZHANG, JIA-MING","ちょうかめい"],
    "ZYT":["張雅婷","ZHANG, YA-TING","ちょうがてい"],
    "ZDQ":["張大謙","ZHANG, DA-QIAN","ちょうだいけん"],
    "HGT":["何耿廷","HE, GENG-TING","かこうてい"],
    "LCH":["梁鈞翔","LIANG, CHUN-HSIANG","りょうきんしょう"],
    "LXW":["呂星緯","LU, XING-WEI","りょせいい"],
    "HTC":["許庭瑊","HSU, TING CHEN","きょていしん"],
}

# print(json.dumps(trans_dict))

# # 上述內容自己產生json檔案
with open("translate.json","w", encoding="utf-8") as f:
    f.write(json.dumps(trans_dict, ensure_ascii=False, indent=4))


#
# with open("translate.json","r") as f :
#     text_open = f.read()

# # text_open = json.loads("translate.json")

# print(text_open)
# print(type(text_open))

# dict_text= json.loads(text_open)
# print(dict_text)
# print(type(dict_text))
