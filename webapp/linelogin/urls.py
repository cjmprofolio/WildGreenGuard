from django.urls import path
from . import views


urlpatterns = [
               path("policy/",views.policy),
               path("profile/",views.profile),
               path('line_login/', views.line_login)
               
               
        ]