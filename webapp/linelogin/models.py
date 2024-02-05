from django.db import models

# Create your models here.


class User(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
