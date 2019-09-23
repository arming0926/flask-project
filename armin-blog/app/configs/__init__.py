from .config import *
from flask import Blueprint

app = Blueprint('main', __name__)

from ..views import index