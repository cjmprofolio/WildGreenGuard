from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image
from flask import Flask, jsonify, request
from flask_cors import CORS
from ultralytics import YOLO


BASE_DIR = Path().cwd()

app = Flask(__name__)
# cross-origin resource sharing
CORS(app)


# set chinese classes name 
classes = [
    '紫花藿香薊','紫花藿香薊花','紫花藿香薊葉',
    '刺莧','刺莧花','刺莧葉',
    '大花咸豐草','大花咸豐草花','大花咸豐草葉','大花咸豐草種子',
    '雞冠花','雞冠花花', '雞冠花葉',
    '孟仁草', '孟仁草花',
    '昭和草','昭和草花', '昭和草葉',
    '牛筋草', '牛筋草花',
    '馬纓丹','馬纓丹花','馬纓丹葉',
    '銀合歡','銀合歡花','銀合歡葉','銀合歡種子',
    '小花蔓澤蘭', '小花蔓澤蘭花','小花蔓澤蘭葉',
    '芒草', '芒草花',
    '象草','象草花',  
    '合果芋',
    '王爺葵','王爺葵花', '王爺葵_葉',
]

# Load the YOLOv8 model
model = YOLO(BASE_DIR/'best.pt')

# classes names
# model.names
# {0: 'Ageratum_houstonianum',
#  1: 'Ageratum_houstonianum_flower',
#  2: 'Ageratum_houstonianum_leaf',
#  3: 'Amaranthus_spinosus',
#  4: 'Amaranthus_spinosus_flower',
#  5: 'Amaranthus_spinosus_leaf',
#  6: 'Bidens_pilosa_var_radiata',
#  7: 'Bidens_pilosa_var_radiata_flower',
#  8: 'Bidens_pilosa_var_radiata_leaf',
#  9: 'Bidens_pilosa_var_radiata_seed',
#  10: 'Celosia_argentea',
#  11: 'Celosia_cristata_flower',
#  12: 'Celosia_cristata_leaf',
#  13: 'Chloris_barbata',
#  14: 'Chloris_barbata_flower',
#  15: 'Crassocephalum_crepidioides',
#  16: 'Crassocephalum_crepidioides_flower',
#  17: 'Crassocephalum_crepidioides_leaf',
#  18: 'Eleusine_indica',
#  19: 'Eleusine_indica_flower',
#  20: 'Lantana_camara',
#  21: 'Lantana_camara_flower',
#  22: 'Lantana_camara_leaf',
#  23: 'Leucaena_leucocephala',
#  24: 'Leucaena_leucocephala_flower',
#  25: 'Leucaena_leucocephala_leaf',
#  26: 'Leucaena_leucocephala_seed',
#  27: 'Mikania_micrantha',
#  28: 'Mikania_micrantha_flower',
#  29: 'Mikania_micrantha_leaf',
#  30: 'Miscanthus_species',
#  31: 'Miscanthus_species_flower',
#  32: 'Pennisetum_purpureum',
#  33: 'Pennisetum_purpureum_flower',
#  34: 'Syngonium_podophyllum',
#  35: 'Tithonia_diversifolia',
#  36: 'Tithonia_diversifolia_flower',
#  37: 'Tithonia_diversifolia_leaf'}

@app.route("/" ,methods=['POST'])
def index():
    if request.method=='POST':
        byte = request.files.get("file").stream.read()
        img_array = preprocessing(byte)
        
        # https://github.com/ultralytics/ultralytics/issues/6969
        # predict the image with confidence threshold
        results = model(img_array, conf=0.6)

        for r in results:
            # replace the classes names 
            for i in r.names.keys():
                r.names[i] = classes[i]

            # plot box on img
            im_array = r.plot()  # plot a BGR numpy array of predictions
            im_list= np.array(im_array).tolist()
            return jsonify({"result": im_list})


# preprocess the input, return array
def preprocessing(input):
    im = Image.open(BytesIO(input))
    im = im.convert("RGB")
    im = im.resize((640, 640))
    img_array = np.array(im)

    return img_array
