from flask import Blueprint

# Initialize the Blueprint
upload_bp = Blueprint('upload_bp', __name__, template_folder='templates')

from . import routes