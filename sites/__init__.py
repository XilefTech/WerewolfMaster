from flask import Blueprint

api = Blueprint('api', __name__, template_folder='templates', static_folder='static')
ui = Blueprint('ui', __name__, template_folder='templates', static_folder='static')

from . import api_routes
from . import ui_routes