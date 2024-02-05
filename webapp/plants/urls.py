from django.urls import path
from . import views
from .views import PredictView

app_name = "plants"

urlpatterns = [
    path("", views.index, name="index"),
    path("identifier", views.identifier, name="identifier"),
    path("developers", views.developer, name="developer"),
    path("FAQ", views.freq_question, name="questions"),
    path('predict/', PredictView.as_view(), name='predict')

]
