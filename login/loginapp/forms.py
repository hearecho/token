from django import forms
from captcha.fields import CaptchaField

from django import forms

class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码')

class RegisterForm(forms.Form):
    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256,min_length=6, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    qq = forms.CharField(label = "QQ",max_length=13,min_length=6,widget=forms.TextInput(attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(label='性别', choices=gender)
    captcha = CaptchaField(label='验证码')

class CginfoForm(forms.Form):
    password1 = forms.CharField(label="密码", max_length=256, min_length=6,widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256,widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码')


class MessageForm(forms.Form):
    title = forms.CharField(label="标题",max_length=256,min_length=1,widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(label="内容",max_length=1000,min_length=0,widget=forms.Textarea(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码')
