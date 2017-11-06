from flask import Flask,flash
from flask import request,session,redirect, url_for
from flask import render_template
from flask import send_file
from werkzeug.security import generate_password_hash,check_password_hash#加密
from wtforms import Form
from flask_wtf import Form
from wtforms.fields import (StringField, PasswordField, BooleanField,
                            SelectField, SelectMultipleField, TextAreaField,
                            RadioField, SubmitField,IntegerField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
import time
import pymysql
import random
import string

#初始化数据库
connect = {
    'host':'localhost',
    'port' : 3306,  
    'user':'root',
    'password':'ssf971114',
    'db':'test',
    'charset':'utf8mb4',
}
db = pymysql.connect(**connect)
cursor = db.cursor()

class Loginform(Form):#登陆类
    username = StringField('用户名',validators=[DataRequired()])
    password = PasswordField('密码',validators=[DataRequired()])
    submit = SubmitField('登陆')

class Registerform(Form):#注册类
    username = StringField('用户名',validators=[Length(min=2,max=20)])
    password = PasswordField('密码',validators=[DataRequired(),EqualTo('confirm',message='Passwords must match')])
    confirm = PasswordField('重复密码')
    email = StringField('邮箱',validators=[Email()])
    qq = StringField('QQ',validators=[Length(min=8,max=12)])
    location = StringField('地址',validators=[DataRequired()])
    img = RadioField('头像',choices=[('images/1.jpg',"<img src=\"../static/images/1.jpg\" width=\"30\" height=\"30\" alt=\"test\"/>"),('images/2.jpg',"<img src=\"../static/images/2.jpg\" width=\"30\" height=\"30\" alt=\"test\"/>")])
    accept_terms = BooleanField('我接受用户协议', default='checked',validators=[DataRequired()])
    submit = SubmitField('注册')

class Cgpassform(Form):#修改信息类
    password = PasswordField('新的密码',validators=[DataRequired(),EqualTo('confirm',message='Passwords must match')])
    confirm = PasswordField('重复密码')
    email = StringField('邮箱')
    qq = StringField('QQ')
    submit = SubmitField('确认')

def enPassWord(password):
    return generate_password_hash(password)
#解析从数据库中得出来的密码
def checkPassWord(enpassword,password):
    return check_password_hash(enpassword,password)
#判断用户是否存在与数据库
def isuserexisted(username):
    sql = 'select username from user'
    cursor.execute(sql)
    results = cursor.fetchall()
    item = (username,)
    if item in results:
        return True
    else:
        return False
#查询用户数据库中的hash值
def checkhash(username):
    sql = 'select password from user where username = \'{}\''.format(username)
    cursor.execute(sql)
    results = cursor.fetchone()[0]
    return results


web = Flask(__name__)
web.secret_key = 'you-never-guess'
StatusCode = False#判别用户登陆状态 全局变量
#首页登录页
@web.route('/home',methods=['GET','POST'])
@web.route('/',methods=['GET','POST'])#登陆界面加主界面
def home():
    session['user'] = ''
    form = Loginform()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if isuserexisted(username):
            pd = checkhash(username)
            if check_password_hash(pd,password):
                session['user'] = username
                session['logged_in'] = True
                if session['user'] != 'admin':
                    sql = 'select * from user where username=\'{}\''.format(str(username))
                    cursor.execute(sql)
                    results = cursor.fetchone()
                    img = "../static/"+str(results[5])
                    return render_template('userdetails.html',form = results,img = img)#登陆成功
                else:
                    flash(" {} 欢迎来到管理员后台".format(session['user']),'message')
                    return redirect('/admin')
            else:
                return render_template('sign.html',flag = True,form = form)#登陆失败返回
        else:
            return render_template('sign.html',flag = True,form = form)#登陆失败返回
    return render_template('sign.html',form=form)

@web.route('/sign',methods=['GET','POST'])#主页到注册页面
def sign():
    form = Registerform()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        pd = enPassWord(password)
        email = form.email.data 
        qq = form.qq.data
        location = form.location.data
        img = form.img.data
        s = (username,)
        sql = 'select username from user where username=\'{}\' '.format(str(username))
        cursor.execute(sql)
        results = cursor.fetchone()
        if s!=results:
            sql = "insert into user(username,password,eamil,QQ,img,location,bianhao) values('{}','{}','{}','{}','{}','{}','{}')".format(username,pd,email,qq,img,location,''.join(random.sample(string.ascii_letters + string.digits, 8)))
            cursor.execute(sql)
            db.commit()
            return redirect('/home')
        else:
            return render_template('signup.html',flag = True,form=form)
    return render_template('signup.html',form = form)

@web.route('/cg',methods=['GET','POST'])#转换到修改信息界面
def cg():
    form = Cgpassform()
    if session['user'] != '':
        if form.validate_on_submit():
            password = enPassWord(form.password.data)
            email = form.email.data
            qq = form.email.data
            d = {'password':password,'eamil':email,'QQ':qq}
            for key,value in d.items():
                if value != '':
                    sql = "update user set {}=\'{}\' where username=\'{}\'".format(key,value,str(session['user']))
                    cursor.execute(sql)
                    db.commit()
                else:
                    continue
            session['user'] = ''
            return redirect('/home')
        return render_template('cgpass.html',form=form)
    else:
        return redirect('/home')

@web.route('/cgm',methods=['GET','POST'])#等会重定向用
def cgm():
    if session['user'] != '':
        if session['user'] == 'admin':
            sql = 'select time,word,bianhao2,audit,name from message'
            cursor.execute(sql)
            results = cursor.fetchall()
            return render_template('cgmessage.html',form=results,flag = True)
        else:
            sql = 'select time,word,bianhao2,audit,name  from message where name=\'{}\' '.format(str(session['user']))
            cursor.execute(sql)
            results = cursor.fetchall()
            return render_template('cgmessage.html',form=results)
    else:
        return redirect('/home') 

@web.route('/cgmessage',methods=['GET','POST'])
def cgmessage():
    if session['user'] != '':
        sql = 'delete from message where bianhao2=\'{}\' '.format(str(request.form['user']),)
        cursor.execute(sql)
        db.commit()
        return redirect('/cgm')
    else:
        return redirect('/home')



@web.route('/deleteuser',methods=['GET','POST'])
def deleteuser():
    sql = "delete from user where username = \'{}\'".format(request.form['user'])
    cursor.execute(sql)
    db.commit()
    sql = "delete from message where name = \'{}\'".format(request.form['user'])#删除用户的同时删除他的全部留言
    cursor.execute(sql)
    db.commit()
    if session['user'] == 'admin':
        return redirect('/admin')
    else:
        return render_template('sign.html')

@web.route('/admin',methods=['GET','POST'])
def admin():
    if session['user'] == 'admin':
        # sql = "select img from user where username = 'admin' "
        # cursor.execute(sql)
        # img = cursor.fetchone()[0]
        return render_template('admin.html')
    else:
        return redirect('/home')

@web.route('/backuser',methods=['GET','POST'])
def backuser():
    if session['user'] != '':
        if session['user'] != 'admin':
            sql = 'select * from user where username=\'{}\''.format(session['user'])
            cursor.execute(sql)
            results = cursor.fetchone()
            img = "../static/"+str(results[5])
            return render_template('userdetails.html',form = results,img = img)
        else:
            return redirect('/admin')
    else:
        return redirect('/home')

@web.route('/message',methods=['GET','POST'])#转换至查看留言与提交留言的界面
def message():
    sql = 'select name,time,word,email,QQ,img,bianhao2 from message where audit = 1 '
    cursor.execute(sql)
    messagedb = cursor.fetchall()
    sql = 'select name,time,word,bianhao2 from commit'
    cursor.execute(sql)
    commitdb = cursor.fetchall()
    if session['user'] != '':
        return render_template('add.html',form=messagedb,form1 =commitdb, flag=True)
    else:
        return render_template('add.html',form=messagedb,form1 =commitdb,flag=False)

@web.route('/direct',methods=['GET','POST'])
def direct():
    sql = 'select name,time,word,email,QQ,img,bianhao2 from message'
    cursor.execute(sql)
    messagedb = cursor.fetchall()
    return render_template('add.html',flag = False,form=messagedb)#非登录状态只能查看留言

@web.route('/commit',methods=['GET','POST'])
def commit():
    ms = request.args.get('ms')
    return render_template('commit.html',ms=ms)

@web.route('/addcommit',methods=['GET','POST'])
def addcommit():
    commit = request.form['commit']
    ua = request.form['ua']
    datatime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if commit != '':
        sql = "insert into commit(name,time,word,bianhao2) values(\'{}\',\'{}\',\'{}\',\'{}\')".format(session['user'],datatime,commit,ua)
        cursor.execute(sql)
        db.commit()
    return redirect('/message')


@web.route('/add',methods=['GET','POST'])
def add():
    if session['user'] != '':
        if request.method == 'POST':
            sql = "select eamil,QQ,img,bianhao from user where username = \'{}\'".format(session['user'])
            cursor.execute(sql)
            results= cursor.fetchone()
            email = results[0]
            QQ  = results[1]
            img = "../static/"+results[2]
            bianhao = results[3]
            datatime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            word = request.form['word']
            if word != '':#检查留言是否为空
                if session['user'] == 'admin':
                    sql = "insert into message(name,word,time,email,QQ,img,bianhao1,bianhao2,audit) values(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',{})".format(session['user'],word,datatime,email,QQ,img,bianhao,''.join(random.sample(string.ascii_letters + string.digits, 4)),1)
                else:
                    sql = "insert into message(name,word,time,email,QQ,img,bianhao1,bianhao2,audit) values(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',{})".format(session['user'],word,datatime,email,QQ,img,bianhao,''.join(random.sample(string.ascii_letters + string.digits, 4)),0)
                cursor.execute(sql)
                db.commit()
            return redirect('/message')
        else:
            sql = 'select name,time,word,email,QQ,img,bianhao2 from message where audit = 1'
            cursor.execute(sql)
            messagedb = cursor.fetchall()
            sql = 'select name,time,word,bianhao2 from commit'
            cursor.execute(sql)
            commitdb = cursor.fetchall()
            return render_template('add.html',form=messagedb,form1 =commitdb,flag=True)
    else:
        return redirect('/message')

@web.route('/audit',methods=['GET','POST'])#转向审核留言窗口
def audit():
    sql = 'select name,word,bianhao2 from message where audit = 0'
    cursor.execute(sql)
    results = cursor.fetchall()
    if session['user'] == 'admin':
        return render_template('audit.html',form=results)
    else:
        redirect('/home')
@web.route('/auditm',methods=['GET','POST'])#执行审核操作
def auditm():
    if session['user'] == 'admin':
        sql = 'update message set audit = 1 where bianhao2 = \'{}\' '.format(request.form['user'])
        cursor.execute(sql)
        db.commit()
        return redirect('/audit')
    else:
        return redirect('/home')

@web.route('/deleteus',methods=['GET','POST'])#admin后台删除用户
def deleteus():
    if session['user'] == 'admin':
        sql = "select username from user"
        cursor.execute(sql)
        results = cursor.fetchall()
        return render_template('deleteuser.html',form=results)
    else:
        return redirect('/home')



@web.route('/logout')#退出登录
def logout():
    session['user'] =''
    session['logged_in'] = False
    return redirect(url_for('home'))


if __name__ == '__main__':
    web.run(host="0.0.0.0",port = 80,debug=True)
    db.close()