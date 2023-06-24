from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Blogs(models.Model):
    user    = models.ForeignKey(User,on_delete=models.CASCADE)
    title   = models.CharField(max_length=100)
    content = models.TextField()
    image   = models.ImageField(upload_to='blog_images')

    def __str__(self):
        return self.title
    

class Comments(models.Model):
    comment = models.CharField(max_length=500)
    user    = models.ForeignKey(User,on_delete=models.CASCADE)
    blog    = models.ForeignKey(Blogs,on_delete=models.CASCADE)

    def __str__(self):
        return self.comment