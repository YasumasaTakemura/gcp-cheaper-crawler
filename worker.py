from flask import Flask
import datetime
import uuid
import tempfile
tempfile.SpooledTemporaryFile = tempfile.TemporaryFile

from app.crawler.view import crawler
app = Flask(__name__)

modules_define = [crawler]
for module in modules_define:
    app.register_blueprint(module)