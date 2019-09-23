from flask import Flask,request,redirect,url_for,abort,jsonify,session
from datetime import timedelta
app = Flask(__name__)

# 设置程序秘钥
app.secret_key = '3edcVGY&'


@app.route('/login')
def login():
    session['logged_in'] = True
    # 设置 session 的有效期，默认 31 天
    session.permanent = True
    # 设置有效期为 10 分钟
    app.permanent_session_lifetime = timedelta(minutes=10)
    return redirect(url_for('hello'))


@app.route('/404')
def not_found():
    abort(404)


@app.route('/')
@app.route('/hello')
def hello():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name','Armin')
        response = '<h1> Hello %s! </h1>' % name
    if 'logged_in' in session:
        response += '[Authenticated 登陆成功]'
    else:
        response = '[Not Authenticated 请先登录]'
    return response

@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('hello'))

@app.route('/greet/')
#@app.route('/greet/<name>')
def greet():
    name = request.args.get('name','Faker')
    return '<h1> Hello %s! </h1>' % name


if __name__ == '__main__':
    app.run(debug=True)
