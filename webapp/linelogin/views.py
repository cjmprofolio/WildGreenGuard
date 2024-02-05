from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.conf import settings
import uuid
import requests
from django.urls import reverse



# Create your views here.

def policy(request):
    return render(request,'linelogin/policy.html')


def profile(request):
    return render(request, 'linelogin/profile.html')
     


def line_login(request):
    # 確認是否為GET請求
    code = request.GET.get('code')
    state = request.GET.get('state')

    # 如果code和state都存在
    if code and state:
        # 使用Django的設定，代替原本Flask配置中的環境變數
        line_login_id = settings.LINE_LOGIN_ID
        line_login_secret = settings.LINE_LOGIN_SECRET
        end_point = settings.LINE_API_END_POINT

        # 進行存取令牌的交換
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f'{end_point}/line_login',
            'client_id': line_login_id,
            'client_secret': line_login_secret
        }
        response = requests.post(
            f'https://api.line.me/v2/oauth/accessToken', headers=headers, data=data)
        response_data = response.json()

        # 使用存取令牌獲取用戶資料
        access_token = response_data['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(
            f'https://api.line.me/v2/profile', headers=headers)
        profile_data = profile_response.json()

        # 從profile_data提取用戶資訊
        user_id = profile_data['userId']
        status_message = profile_data.get('statusMessage')
        display_name = profile_data['displayName']

        # 渲染模板並回應
        context = {
            'name': display_name,
            'user_id': user_id,
            'status_message': status_message
        }
        response = render(request, 'linelogin/profile.html', context)

        response.set_cookie('client_id', 'client_id_value', max_age=14*24*3600)  

        return response

    else:
        # 如果不是GET請求或者缺少參數，重定向到登入頁面
        return redirect('linelogin/policy.html')  # 假設 'login_url' 是登入頁面的URL名稱
