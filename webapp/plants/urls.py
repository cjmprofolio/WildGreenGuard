from django.urls import path
from . import views

app_name= "plants"

urlpatterns = [
    path("", views.index, name="index"),
<<<<<<< HEAD
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
=======
    path("identifier", views.identifier, name="identifier"),
    path("developers", views.developer, name="developer"),
    path("FAQ", views.freq_question, name="questions"),
>>>>>>> 9a81ffd551d3acb05b5fc57da2c1d484dd14adea
]