from django.shortcuts import render,redirect,render_to_response
from django.db import models
from django import forms
from loginapp import forms,models
import hashlib
import time
# Create your views here.

def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()
def index(request):
    messages = models.Message.objects.all()
    # login_form = forms.UserForm()
    return render(request, 'loginapp/index.html',{'messages':messages})

#登陆部分
def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    # messages = models.Message.objects.all()
                    return redirect('/index')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'loginapp/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'loginapp/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            qq = register_form.cleaned_data['qq']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'loginapp/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'loginapp/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'loginapp/register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = hash_code(password1)  # 使用加密密码
                new_user.email = email
                new_user.qq = qq
                new_user.sex = sex
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    register_form = forms.RegisterForm()
    return render(request, 'loginapp/register.html', locals())

def perinfo(request):
    if not request.session.get('is_login', None):
        return redirect("/index")
    username = request.session['user_name']
    perinfo = models.User.objects.filter(name=username)
    return render(request,"loginapp/perinfo.html",{'perinfo':perinfo[0]})

def cginfo(request):
    if not request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'loginapp/cginfo.html', locals())
            else:
                username = request.session['user_name']
                user = models.User.objects.filter(name=username)
                user.password = hash_code(password1)
                user.save()
                del request.session['is_login']
                del request.session['user_id']
                del request.session['user_name']
                return redirect('/login/')
    cginfo_form = forms.CginfoForm()
    return render(request, 'loginapp/cginfo.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    return redirect("/index/")

#留言部分
# def showallms(request):#显示全部留言
#     messages = models.Message.objects.all()
#     return render(request, "loginapp/index.html", {'message': messages})

def pubms(request):
    if not request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        pubms_form = forms.MessageForm(request.POST)
        message = "请检查填写的内容！"
        if pubms_form.is_valid():
            title = pubms_form.cleaned_data['title']
            content = pubms_form.cleaned_data['content']
            id=request.session['user_id']
            pub_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            new_message = models.Message(perinfo_id =id ,title=title,content=content,pub_time=pub_time)
            new_message.save()
            return redirect('/index')
    pubms_form = forms.MessageForm()
    return render(request,'Message/PubMessage.html',locals())



def showselfms(request):
    if not request.session.get('is_login', None):
        return redirect("/index/")
    username = request.session['user_name']
    # user = models.User.objects.get(name=username)
    messages = models.Message.objects.filter(perinfo__name = username)
    return render(request, 'Message/SelfMessage.html',{'messages':messages})

def delselfms(request):
    if not request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        id = request.POST.getlist('data')[0]
        delms = models.Message.objects.filter(id=id)
        delms.delete()
        return redirect('/showselfms')
    pass
