from flask import Flask,flash
from flask import request,session,redirect, url_for
from flask import render_template
from flask import send_file
from werkzeug.security import generate_password_hash,check_password_hash#加密
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
# 该表储存留言
 # sql = '''CREATE TABLE IF NOT EXISTS message (
 #         id int(11) not null auto_increment,
 #         name char(255) default null,
 #         word text(1000) default null,
 #         time char(255) default null,
 #         email char(255) default null,
 #         QQ char(255) default null,
 #         img char(255) default null, 
 #         bianhao1 char(20) default null,
 #         bianhao2 char(20) default null,
 #         audit int(11) default null,
 #         primary key(id)
 #           )engine = innodb;
 #        '''
 #与用户表连接
# cursor.execute(sql)
# db.commit()
# sql1 = '''CREATE TABLE IF NOT EXISTS user (#该表存储个人信息
#             userid int(11) not null auto_increment,
#             username char(255) default null,
#             password char(255) default null,
#             eamil char(255) default null,
#             QQ char(255) default null,
#             img char(255) default null,
#             location char(255) default null,
#             bianhao1 char(20) default null,
#             primary key(userid)
#             )engine = innodb;
#         '''
#两个表之间通过编号联系，每个用户注册时随机生成一个编号

#加密函数
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
    return render_template('sign.html')

@web.route('/sign',methods=['GET'])#主页到注册页面
def sign():
    return render_template('signup.html')

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

@web.route('/signup',methods=['GET','POST'])#注册成功后转到登陆界面
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pd = enPassWord(password)#进行加密处理
        email = request.form['email']
        qq = request.form['qq']
        location = request.form['location']
        img = request.form['img']
        if not (password and username):
            return render_template('signup.html')#用户名和密码不能为空
        s = (username,)
        sql = 'select username from user where username=\'{}\' '.format(str(username))
        cursor.execute(sql)
        results = cursor.fetchone()
        if s!=results:#判断是否存在
        	# salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))随机字符串编号
            sql = "insert into user(username,password,eamil,QQ,img,location,bianhao) values('{}','{}','{}','{}','{}','{}','{}')".format(username,pd,email,qq,img,location,''.join(random.sample(string.ascii_letters + string.digits, 8)))
            cursor.execute(sql)
            db.commit()
            return render_template('sign.html')
        else:
            return render_template('signup.html',flag = True)
    if request.method == 'GET':
        return render_template('signup.html')


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

@web.route('/signin',methods=['GET','POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
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
            return render_template('sign.html',flag = True)#登陆失败返回
    else:
        return render_template('sign.html',flag = True)#登陆失败返回

@web.route('/cg',methods=['GET','POST'])#转换到修改信息界面
def cg():
    if session['user'] != '':
        return render_template('cgpass.html')
    else:
        return redirect('/home')

@web.route('/cgpass',methods=['GET','POST'])#修改信息
def cgpass():
    if session['user']!='':
        password = enPassWord(request.form['password'])
        email = request.form['email']
        qq = request.form['qq']
        # if password and email and qq:
        #     sql = '''update user set password=\'{}\',eamil=\'{}\',QQ=\'{}\' where username = \'{}\';'''.format(password,email,qq,str(session['user']))
        #     cursor.execute(sql)
        #     db.commit()
        #     return render_template('sign.html')
        # else:
        #     return render_template('cgpass.html')
        d = {'password':password,'eamil':email,'QQ':qq}
        if password != '':
            for key,value in d.items():
                if value != '':
                    sql = "update user set {}=\'{}\' where username=\'{}\'".format(key,value,str(session['user']))
                    cursor.execute(sql)
                    db.commit()
                else:
                    continue
            return redirect('/home')
        else:
            return redirect('/cg')
    else:
        return render_template('sign.html')

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
    if session['user'] != '':
        return render_template('add.html',form=messagedb,flag=True)
    else:
        return render_template('add.html',form=messagedb,flag=False)

@web.route('/direct',methods=['GET','POST'])
def direct():
    sql = 'select name,time,word,email,QQ,img from message'
    cursor.execute(sql)
    messagedb = cursor.fetchall()
    return render_template('add.html',flag = False,form=messagedb)#非登录状态只能查看留言

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
            sql = "insert into message(name,word,time,email,QQ,img,bianhao1,bianhao2,audit) values(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',{})".format(session['user'],word,datatime,email,QQ,img,bianhao,''.join(random.sample(string.ascii_letters + string.digits, 4)),0)
            cursor.execute(sql)
            db.commit()
            return redirect('/message')
        else:
            sql = 'select name,time,word,email,QQ,img,bianhao2 from message where audit = 1'
            cursor.execute(sql)
            messagedb = cursor.fetchall()
            return render_template('add.html',form=messagedb,flag=True)
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