from flask import Flask, request,Blueprint
import datetime

extractor = Blueprint('parser', __name__)


@extractor.route('/extract_html')
def extract_html():
    print('========== start connection ===========')
    
    return '', 200
