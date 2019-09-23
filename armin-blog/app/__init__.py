# coding=utf-8
from flask import Flask


def create_app(config_name):
    """创建flask应用app对象"""
    app = Flask(__name__)

    from .configs import app as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
