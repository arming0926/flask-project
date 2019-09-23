import re
import pymysql
import datetime
from ..configs import app
from flask import flash, render_template, request, session
from app.models.my_sql import *
from functools import wraps
from app.spiders.my_spider import Spider


def is_login(f):
    """用来判断用户是否登录成功"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        # 判断session对象中是否有seesion['user'],
        # 如果包含信息， 则登录成功， 可以访问主页；
        # 如果不包含信息， 则未登录成功， 跳转到登录界面;；
        if session.get('user', None):
            return f(*args, **kwargs)
        else:
            flash("请登录后再访问博客主页", 'login')
            return render_template('homepage.html')

    return wrapper


# 主页

@app.route('/')
def index():
    return render_template('homepage.html')


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        tel = request.form['tel']
        password = request.form['password']

        # 登陆
        # 首先校验参数是否完整，包括手机号和密码
        if not all([tel, password]):
            print("登陆参数不完整")
            return render_template('login.html', msg='登陆参数不完整')

        # 进一步校验具体的每个参数，手机号格式
        if not re.match(r"^1[34578]\d{9}$", tel):
            print("手机号格式错误")
            return render_template('login.html', msg='手机号格式错误')

        # 查询数据库操作，对手机号进行进一步验证
        user_login = check_mysql('verify_users', 'id,password', where='tel="%s"' % tel)
        if not len(user_login):
            print("账号不存在")
            return render_template('login.html', msg='账号不存在')

        check_password = user_login[0][1]
        if check_password != password:
            print("密码错误")
            return render_template('login.html', msg='密码错误')

        Spider(tel, password)
        session['user'] = tel

        return render_template('success.html')


# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        tel = request.form['tel']
        password = request.form['password']

        # 登陆
        # 首先校验参数是否完整，包括手机号和密码
        if not all([tel, password]):
            print("注册参数不完整")
            return render_template('register.html', msg='注册参数不完整')

        # 进一步校验具体的每个参数，手机号格式
        if not re.match(r"^1[34578]\d{9}$", tel):
            print("手机号格式错误")
            return render_template('register.html', msg='手机号格式错误')
        user_login = check_mysql('verify_users', 'id,password', where='tel="%s"' % tel)
        if len(user_login):
            print("账号已存在")
            return render_template('register.html', msg='账号已存在')

        # 数据库操作，注册账户
        save_mysql('verify_users', {'tel': tel, 'password': password})
        session['user'] = tel
        return render_template('success.html')


# 新建日志
@app.route('/create_blog', methods=['GET', 'POST'])
@is_login
def create_blog():
    if request.method == 'GET':
        return render_template('create_blog.html')

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = request.form['content']
        blog_content = check_mysql('user_blog', 'title,author,update_time,content', where='title="%s"' % title)
        if blog_content:
            print("标题已存在，请重新输入")
            return render_template('create_blog.html', msg='标题已存在，请重新输入')
        # 数据库操作，注册账户
        save_mysql('user_blog', {'title': title, 'author': author, 'update_time': update_time,
                                 'content': pymysql.escape_string(content)})

    blog_content = check_mysql('user_blog', 'title,author,update_time,content')
    print(blog_content)
    blog_rows = []
    for i in blog_content:
        blog_dict = {}
        blog_dict['title'] = i[0]
        blog_dict['author'] = i[1]
        blog_dict['update_time'] = i[2]
        blog_dict['content'] = i[3]
        blog_rows.append(blog_dict)
    if blog_rows:
        flash('创建日志成功', 'ok')

    return render_template('blog_content.html', blog_rows=blog_rows)


# 删除指定的日志
@app.route('/delete_blog/<title>', methods=['GET'])
@is_login
def delete_blog(title):
    delete_mysql('user_blog', where='title="%s"' % title)

    blog_content = check_mysql('user_blog', 'title,author,update_time,content')
    blog_rows = []
    for i in list(blog_content):
        blog_dict = {}
        blog_dict['title'] = i[0]
        blog_dict['author'] = i[1]
        blog_dict['update_time'] = i[2]
        blog_dict['content'] = i[3]
        blog_rows.append(blog_dict)
    print(blog_rows)
    flash("删除日志成功!", 'ok')
    return render_template('blog_content.html', blog_rows=blog_rows)


# 删除全部日志
@app.route('/delete_all_blog', methods=['GET'])
@is_login
def delete_all_blog():
    delete_mysql('user_blog')

    blog_content = check_mysql('user_blog', 'title,author,update_time,content')

    blog_rows = []
    for i in list(blog_content):
        blog_dict = {}
        blog_dict['title'] = i[0]
        blog_dict['author'] = i[1]
        blog_dict['update_time'] = i[2]
        blog_dict['content'] = i[3]
        blog_rows.append(blog_dict)
    print(blog_rows)
    flash("成功删除所有日志!", 'ok')
    return render_template('blog_content.html', blog_rows=blog_rows)


# 修改日志
@app.route('/update_blog/<title>', methods=['GET', 'POST'])
@is_login
def update_blog(title):
    if request.method == 'GET':
        blog_content = check_mysql('user_blog', 'title,author,content', where='title="%s"' % title)

        blog_rows = []
        for i in list(blog_content):
            blog_dict = {}
            blog_dict['title'] = i[0]
            blog_dict['author'] = i[1]
            blog_dict['content'] = i[2]
            blog_rows.append(blog_dict)
        return render_template('update_blog.html', blog_rows=blog_rows)

    if request.method == 'POST':
        new_title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        update_mysql('user_blog', {'title': new_title, 'author': author, 'content': pymysql.escape_string(content)},
                     where='title="%s"' % title)
        blog_content = check_mysql('user_blog', 'title,author,update_time,content', where='title="%s"' % new_title)
        blog_rows = []
        for i in blog_content:
            blog_dict = {}
            blog_dict['title'] = i[0]
            blog_dict['author'] = i[1]
            blog_dict['update_time'] = i[2]
            blog_dict['content'] = i[3]
            blog_rows.append(blog_dict)
        if blog_rows:
            flash('修改日志成功', 'ok')
        return render_template('blog_detail.html', blog_rows=blog_rows)


# 退出
@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return render_template('homepage.html')


# 日志详情页
@app.route('/blog_detail/<title>', methods=['GET'])
@is_login
def blog_detail(title):
    if request.method == 'GET':
        blog_content = check_mysql('user_blog', 'title,author,update_time, content', where='title="%s"' % title)

        blog_rows = []
        for i in list(blog_content):
            blog_dict = {}
            blog_dict['title'] = i[0]
            blog_dict['author'] = i[1]
            blog_dict['update_time'] = i[2]
            blog_dict['content'] = i[3]
            blog_rows.append(blog_dict)
        print(blog_rows)
        return render_template('blog_detail.html', blog_rows=blog_rows)


# 未登录页
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


# 登录成功页
@app.route('/success')
@is_login
def success():
    return render_template('success.html')


# 我的日志
@app.route('/watchlist')
@is_login
def watchlist():
    blog_content = check_mysql('user_blog', 'title,author,update_time,content')
    print(blog_content)
    print(type(blog_content))
    blog_rows = []
    for i in list(blog_content):
        blog_dict = {}
        blog_dict['title'] = i[0]
        blog_dict['author'] = i[1]
        blog_dict['update_time'] = i[2]
        blog_dict['content'] = i[3]
        blog_rows.append(blog_dict)
    print(blog_rows)

    return render_template('blog_content.html', blog_rows=blog_rows)


# 我的相册
@app.route('/picture')
@is_login
def picture():
    return render_template('picture.html')


# 个人资料
@app.route('/personal')
@is_login
def personal():
    blog_content = check_mysql('personal_info', 'name,sex,age, nation,address,email,wechat,hobby')
    personal_rows = []
    for i in list(blog_content):
        personal_dict = {}
        if i[0] == None:
            personal_dict['name'] = ''
        else:
            personal_dict['name'] = i[0]
        personal_dict['sex'] = i[1]
        personal_dict['age'] = i[2]
        personal_dict['nation'] = i[3]
        personal_dict['address'] = i[4]
        personal_dict['email'] = i[5]
        personal_dict['wechat'] = i[6]
        personal_dict['hobby'] = i[7]
        personal_rows.append(personal_dict)
    print(personal_rows)
    return render_template('personal.html', personal_rows=personal_rows)


# 修改个人资料
@app.route('/update_personal/<name>', methods=['GET', 'POST'])
@is_login
def update_personal(name):
    if request.method == 'GET':
        blog_content = check_mysql('personal_info', 'name,sex,age, nation,address,email,wechat,hobby',
                                   where='name="%s"' % name)
        personal_rows = []
        for i in list(blog_content):
            personal_dict = {}
            personal_dict['name'] = i[0]
            personal_dict['sex'] = i[1]
            personal_dict['age'] = i[2]
            personal_dict['nation'] = i[3]
            personal_dict['address'] = i[4]
            personal_dict['email'] = i[5]
            personal_dict['wechat'] = i[6]
            personal_dict['hobby'] = i[7]
            personal_rows.append(personal_dict)
        print(personal_rows)
        return render_template('update_personal.html', personal_rows=personal_rows)
    if request.method == 'POST':
        new_name = request.form['name']
        sex = request.form['sex']
        age = request.form['age']
        nation = request.form['nation']
        address = request.form['address']
        email = request.form['email']
        wechat = request.form['wechat']
        hobby = request.form['hobby']
        update_mysql('personal_info',
                     {'name': new_name, 'sex': sex, 'age': age, 'nation': nation, 'address': address, 'email': email,
                      'wechat': wechat, 'hobby': pymysql.escape_string(hobby)},
                     where='name="%s"' % name)
        blog_content = check_mysql('personal_info', 'name,sex,age, nation,address,email,wechat,hobby',
                                   where='name="%s"' % new_name)
        personal_rows = []
        for i in list(blog_content):
            personal_dict = {}
            personal_dict['name'] = i[0]
            personal_dict['sex'] = i[1]
            personal_dict['age'] = i[2]
            personal_dict['nation'] = i[3]
            personal_dict['address'] = i[4]
            personal_dict['email'] = i[5]
            personal_dict['wechat'] = i[6]
            personal_dict['hobby'] = i[7]
            personal_rows.append(personal_dict)
        if personal_rows:
            flash('修改个人资料成功', 'ok')
        return render_template('personal.html', personal_rows=personal_rows)


# app_errorhandler：全局错误映射
# errorhandler：指定蓝图下错误映射
# 页面没有被找到
@app.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 服务器内部错误
@app.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/test_page')
def test_page():
    return render_template('test_page.html')
