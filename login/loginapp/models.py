from django.db import models

# Create your models here.
class User(models.Model):
    gender = (
        ('male','男'),
        ('female', '女'),
    )
    name = models.CharField(max_length=128,unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    qq = models.CharField(max_length=13,unique=False)
    sex = models.CharField(max_length=32, choices=gender, default="男")
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-c_time']
        verbose_name = "用户"
        verbose_name_plural = "用户"

class Message(models.Model):
    perinfo = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=512)
    content = models.TextField(max_length=256)
    pub_time = models.DateTimeField(auto_now_add=True)

    #显示
    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-pub_time"]
        verbose_name = '留言'
        verbose_name_plural = '留言'

# class Comment(models.Model):
#     message = models.ForeignKey(Message,on_delete=models.CASCADE)



