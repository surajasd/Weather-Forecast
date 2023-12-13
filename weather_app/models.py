from django.db import models

class User(models.Model):
   username = models.CharField(max_length=30) 
   class Meta:
     managed = False
     db_table = 'auth_user'

class Favorites(models.Model):
    city = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'favourites'

class Subscribe(models.Model):
    user_id = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'subscribe'