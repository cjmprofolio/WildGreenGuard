from django.urls import path
from . import views

app_name= "plants"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
]