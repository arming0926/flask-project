from app import create_app

# from flask import Flask, session

app = create_app('default')
# 设置程序秘钥
app.config['SECRET_KEY'] = '3edcVGY&'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
