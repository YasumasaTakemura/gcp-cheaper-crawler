# -*- coding: utf-8 -*-
from flask import request, Blueprint
from app.crawler.crawler import RequestHandler
from app.crawler.crawler import URLHandler
from app.crawler.crawler import notify_ready as notify_ready_
from app.crawler.constants import State
from app.parser.parser import HTMLParse
from app.queue import queue
import os
import logging
logging.basicConfig( filename='/gae.log', filemode='a' )

storage = Blueprint('storage', __name__)


@storage.route('/StoreHTML', methods=['POST', 'GET'])
def store_html():
    """ run start crawling
        usually this method called once
        if you call this method once again , it may happen something like crawler shut down
    """
    print('==========STORE_HTML===========')
    # if request.method == "POST":
    token = request.json.get('token')
    key = request.json.get('key')
    html = request.json.get('html')
    path = 'test-tv-crawler'
    fullpath = os.path.join(path, key, '.gz')
    handler = RequestHandler('')
    keys = handler.store_html(fullpath, html)
    queue.parse_page(fullpath)
    # handler.manager.update_state(urls,status_code,State.URL_STORED)
    print keys

    return str(keys), 200
