from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import render
from .models import Plant, Record
import json
import numpy as np
import requests
from PIL import Image
from django.http import JsonResponse
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

# Create your views here.


def identifier(request):
    """
    Return image and inference or return upload button
    """
    if request.method == 'POST':
        # 取得上傳的圖片
        upload_img = request.FILES.get('image_input')

        # 創建 Plant 模型的實例
        # 假設你已經有了 species_chi 和 species_en 的資料
        species_chi = '輸入的中文名稱'  # 這部分應該由表單或者其他方式獲得
        species_en = 'Input English Name'  # 同上
        isinvasive = False  # 或根據實際情況設定

        # 儲存 Plant 實例
        plant_instance = Plant(
            species_img=upload_img,
            species_chi=species_chi,
            species_en=species_en,
            isinvasive=isinvasive,
            description='描述'  # 這部分應該由表單或其他方式獲得
        )
        plant_instance.save()
    if request.method == "POST":
        print("post")
        # print(request.FILES.get("image_input"))
        upload_img = request.FILES.get("image_input")

        data = {"image": upload_img, "species": "frog", "invasion": False}
        instance = Record(**data)
        try:
            instance.full_clean()
        except ValidationError as e:
            print(e.message_dict)

        instance.save()

        image = instance.image

        return render(request, "plants/identifier.html", {"image": image})

        # 創建 Record 模型的實例
        record_instance = Record(
            uploading=upload_img,
            species=plant_instance
        )
        record_instance.save()

        # 返回一個響應或重定向
        return HttpResponse('圖片上傳成功！')
    else:
        # 如果不是 POST 請求，顯示上傳按鈕
        return render(request, 'plants/index.html')


def about(request):
    # Your logic here
    return render(request, 'plants/about.html')


def services(request):
    # Your logic here
    return render(request, 'plants/services.html')


def faq(request):
    # Your logic here
    return render(request, 'plants/faq.html')


def contact(request):
    # Your logic here
    return render(request, 'plants/contact.html')


# return yolov8 present model
def rt_identifier(request):
    pass

# set index


def index(request):
    return render(request, "plants/index.html")

# retrieve records


def records(request):
    pass

# list all available species


def plants(request):
    pass

# list all developers


def developer(request):
    return render(request, "plants/developers.html")

# list all frequent asked questions


def freq_question(request):
    return render(request, "plants/freq_questions.html")


def developer(request):
    return render(request, 'plants/developers.html')


class PredictView(View):
    def post(self, request, *args, **kwargs):
        # 從表單數據中獲取上傳的文件
        file = request.FILES['file']

        # 使用Pillow轉換圖像格式為JPG
        image = Image.open(file)
        rgb_im = image.convert('RGB')  # 轉換為RGB模式，以確保是JPG格式
        temp_file = default_storage.save('temp.jpg', ContentFile(b''))
        temp_file_path = default_storage.path(temp_file)
        rgb_im.save(temp_file_path, format='JPEG')

        # 讀取轉換後的圖片並進行處理，以便發送
        with open(temp_file_path, 'rb') as image_file:
            # 假設使用numpy將圖片轉換為模型需要的輸入格式
            # 這裡需要根據您的模型進行相應的調整
            batched_img = np.array(rgb_im)

        # 預備發送的數據
        data = json.dumps({
            "signature_name": "serving_default",
            "instances": batched_img.tolist(),
        })

        # 設置目標URL
        url = settings.TENSORFLOW_SERVING_URL
        # 發送POST請求到服務器
        json_response = requests.post(url, data=data)
        response = json.loads(json_response.text)

        # 從服務器響應中提取預測結果

        rest_outputs = np.array(response['predictions'][0])

        # 取得機率最高的類別索引
        predicted_class_index = rest_outputs.argmax()

        # 嘗試取得對應的植物類別，如果不存在則返回"未知類別"
        try:
            plant = Plant.objects.get(id=predicted_class_index + 1)  # 假設id從1開始
            predicted_class = plant.species_en
        except Plant.DoesNotExist:
            predicted_class = "未知類別"

        # 清理臨時文件
        default_storage.delete(temp_file_path)

        # 返回JSON回應
        return JsonResponse({
            'rest_output_shape': rest_outputs.shape,
            'predicted_class': predicted_class
        })