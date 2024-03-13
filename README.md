# WildGreenGuard

- [WildGreenGuard](#wildgreenguard)
  - [Result Preview](#result-preview)
  - [Object](#object)
  - [Invasive plants candidate](#invasive-plants-candidate)
    - [Plan](#plan)
    - [Actual](#actual)
  - [Flow](#flow)
    - [Plan](#plan-1)
    - [Actual](#actual-1)
  - [System design](#system-design)
  - [Database Design](#database-design)
  - [Members](#members)
  - [Jobs](#jobs)
  - [Brief Summary](#brief-summary)
  - [References](#references)

## Result Preview
[![Presentation Video](https://img.youtube.com/vi/UHT4iaAthT8/0.jpg)](https://youtu.be/UHT4iaAthT8)

## Object

- Currently,
  - Invaded species have been problems for a long time. 
  - Though, some apps provide servers But plants 
  - Gain more public attention on the invaded species.

- Our project tries to 
  - Identify the uploaded plant image species 
  - Real-time identify plants


## Invasive plants candidate

### Plan
|入侵種|相似植物|note|
|-|-|-|
|銀合歡||資料庫|
|銀膠菊||資料庫|
|小花蔓澤蘭||拍攝|
|象草|芒草|拍攝|
|大花咸豐草||拍攝|
|孟仁草||拍攝|
|加拿大蓬|野茼蒿|拍攝|
|巴拉草|星草, 牛筋草|拍攝|
|星草|巴拉草, 牛筋草|拍攝|
|粗毛小米菊|長柄菊|拍攝|
|昭和草|
|豬草|

### Actual
|物種名稱|是否為入侵種|相似植物|
|-|:-:|-|
|紫色霍香薊|O||
|大花咸豐草|O||
|雞冠花|O||
|孟仁草|O||
|昭和草|O||
|馬櫻丹|O||
|銀合歡|O||
|小花蔓澤蘭|O||
|象草|O|芒草|
|合果芋|O||
|王爺葵|O||
|刺莧|X||
|芒草|X|象草|
|牛筋草|X||


## Flow

### Plan

1. 
    1. Webscrap images of species listed in [database](https://gisd.biodiv.tw/tw/).
    2. Take the photos Manually.
2. _(choose one)_
    1. Use [Roboflow](https://roboflow.com/) to annotate the roi, then export the yolov8.yml for training.
    2. Use [LabelImg](https://github.com/HumanSignal/labelImg) to annotate the roi, then export the .xml file for training.
3. _(choose one)_
    1. Apply the data into keras [YOLOV8Detector](https://keras.io/api/keras_cv/models/tasks/yolo_v8_detector/).
    2. Apply the data into [Ultralytics](https://docs.ultralytics.com/).
4. _(choose one or both)_
    1. Connect the model to [Line bot](https://github.com/line/line-bot-sdk-python) for using.
    2. Connect to web [Django](https://www.djangoproject.com/) for using. (
   [tensorflow.js](https://js.tensorflow.org/api/latest/#Tensors), [tensorflow.js_Basic use](https://www.tensorflow.org/js/tutorials/conversion/import_keras, ), [onnx.js](https://onnxruntime.ai/docs/api/js/index.html))
    3. Perform the model on edge device with [tensorflow lite](https://www.tensorflow.org/lite).  


### Actual

1. Collecting data  
   Mostly take plant photos by ourselves.
   Test our training model with online public photos.   
  
2. Labelling images  
   Use [Roboflow](https://roboflow.com/) to annotate the roi, then export the yolov8.yml for training.

3. Training model  
   - Rotate and resize images for multi-label classification.
   - Apply the data into [Ultralytics](https://docs.ultralytics.com/)  and train the yolo model.  

4. Application  
    - Connect the model to [Line bot](https://github.com/line/line-bot-sdk-python) for using.
    - Connect to web [Django](https://www.djangoproject.com/) for using.
    - Using [TFserving](https://www.tensorflow.org/tfx/serving/docker) to serve the multi-label classification.
    - Using Flask to serve the yolo model. 

## System design

![system diagram](./images/System%20Diagram.png)

## Database Design

![database diagram](./images/Database%20Diagram.png)

## Members

Leader: 17_張家銘   
Members: 04_梁鈞翔, 12_許庭瑊, 16_呂星緯, 22_張雅婷, 31_何耿廷, 34_張大謙 

## Jobs
|Job|Subgroup Leader|Subgroup Members|
|-|-|-|
|Collect data|17_張家銘|@All|
|Build Model|04_梁鈞翔|31_何耿廷|
|Build Linebot|12_許庭瑊|22_張雅婷|
|Build Web|16_呂星緯|34_張大謙|
|Cloud deploy|22_張雅婷|12_許庭瑊, 16_呂星緯|

## Brief Summary
(2023/12/18~2024/02/06)
- Done  
  - Number of Photos is now 5481. 
  - Line app with identification and lookup functions.
  - Web app with identification, FAQ and line login functions.
  - Line app, mysql, tensorflow/serving and mongodb are online. DNS and GCP load balancing worked.
  - Apply yolo model function with photo.
  - Choose 5 keras pretrained models for evaluation. Current we use vgg19 for inference.
- Ahead
  - Number of photos of each species should be at least 350, 500 is best.
  - Mongodb structure should be arrange.
  - Mysql data should write into mysql in GCP VM.
  - Line links (FAQ, Developers and Go web) to web.
  - Web sub pages (index, diagram, records).
  - Web line login need get userid of line message api, now is not the same.
  - Load balancing connection.
  - yolo application need streaming.


## References

1. [台灣物種名錄](https://taicol.tw/zh-hant/)
2. [認識植物](http://kplant.biodiv.tw/) 
3. [農業知識入口網](https://kmweb.moa.gov.tw/)
4. [Global Core Biodata Resource (GBIF)](https://www.gbif.org/zh-tw/)  
<!-- https://www.imageclef.org/PlantCLEF2020
[銀膠菊與艾草的差異(107/6/23)](https://youtu.be/-tp9ENdx8-k) -->
