from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import render
from .models import Plant, Record

# Create your views here.

def identifier(request):
    """
    Return image and inference or return upload button
    """
<<<<<<< HEAD
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
=======
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
        
        return render(request, "plants/identifier.html", {"image":image})
>>>>>>> 9a81ffd551d3acb05b5fc57da2c1d484dd14adea

        # 創建 Record 模型的實例
        record_instance = Record(
            uploading=upload_img,
            species=plant_instance
        )
        record_instance.save()

        # 返回一個響應或重定向
        return HttpResponse('圖片上傳成功！')
    else:
<<<<<<< HEAD
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
=======
        return render(request, "plants/identifier.html")

    return HttpResponse("ok")
>>>>>>> 9a81ffd551d3acb05b5fc57da2c1d484dd14adea

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
     return render(request,'plants/developers.html')