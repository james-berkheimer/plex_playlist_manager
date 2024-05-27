from flask import Blueprint

auth = Blueprint("authentication", __name__)

from . import routes
