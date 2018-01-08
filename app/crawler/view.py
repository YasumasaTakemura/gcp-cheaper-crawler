# -*- coding: utf-8 -*-
from flask import request, Blueprint
from app.crawler.crawler import RequestHandler
from app.crawler.crawler import URLHandler
from app.crawler.crawler import QuiteManager
from app.crawler.crawler import notify_ready as notify_ready_
from app.uploader import uploader
from app.crawler.constants import State
from app.parser.parser import HTMLParse
from app.uploader.uploader import gcs_path_generator
from app.queue import queue
import datetime
import logging
from app.tasklet import tasklet

logging.basicConfig(filename='/gae.log', filemode='a')

crawler = Blueprint('crawler', __name__)


@crawler.route('/PullUrls', methods=['POST', 'GET'])
def pull_urls():
    """ run start crawling
        usually this method called once
        if you call this method once again , it may happen something like crawler shut down
    """
    print('==========START CRAWLING===========')
    quitManager = QuiteManager()
    if quitManager.is_quiting():
        print '==========Quit command accepted===========\n'
        return '', 200

    req = request.json
    if req:
        url = req.get('url')
        token = req.get('token')
    handler = URLHandler()
    handler.pull_urls()
    entities = handler.entities

    if not entities:
        print '==========No URLs to crawl===========\n'
        return '', 200

    for entity in entities:
        task = queue.request_page(entity.url)
    return '==========Pull URLs Finished===========\n', 200


@crawler.route('/RequestPage', methods=['POST'])
def request_page():
    """ run start crawling
        usually this method called once
        if you call this method once again , it may happen something like crawler shut down
    """
    print('==========START Requesting===========')
    if request.method == "POST":
        req = request.form
        url = req.get('url')
        token = req.get('token')

        if not url:
            print 'No url passed'
            raise KeyError('No url passed')

        handler = RequestHandler(url)
        response = handler.get_page()
        if response.state != State.CRAWLED:
            handler.manager.update_state(response)
            return 'URL : {} Can NOT be crawled properly'.format(url), 200

        # extract urls when 200 returned
        paths = handler.extract_url(response.body)
        # remove duplicated url
        urls = list(set(map(lambda p: tasklet.join_url(handler.domain, p), paths)))

        if not urls:
            return '=========No URLs Found========='

        key = handler.manager.generate_key(url)
        bucket_name = 'tripadvisor-html'
        gcs_path = gcs_path_generator(bucket_name,key)
        closed = uploader.upload_to_gcs(str(gcs_path), response.body)
        print closed
        URLHandler.store_urls(urls, status_code=State.URL_STORED.value, state=State.URL_STORED.value)
        print '=====store_urls is succeeded===='
        key = URLHandler.update_state(url, response.status_code, response.state.value)
        print '=====update_state is succeeded===='
        print key

        if not key:
            print '=====UPDATE_STATE IS FAILED===='
            return '',200

        response = notify_ready_()
        # task = queue.store_html(response.body,bucket_name, key)
        # task = queue.store_html('<html>thisisatesttext</html>', key)
        # task = queue.store_url(url, urls, response.status_code, response.state.value)
        handler.wait()
        print '---------------------'
        print response.status_code
        print response.state
        print '***********************', 200
        return '***********************', 200
        # return 'url : {} , status_code : {} added'.format(url,response.status_code), 200

    print '++++++++++++++'
    return 'wrong method', 200


@crawler.route('/StoreURL', methods=['POST'])
def store_url():
    """ run start crawling
        usually this method called once
        if you call this method once again , it may happen something like crawler shut down
    """
    print('==========STORE_URLS===========')
    if request.method == "POST":
        # token = request.form.get('token')
        url = request.form.get('url')
        urls = request.form.getlist('urls')
        state = request.form.get('state')
        status_code = request.form.get('status_code')
        keys = URLHandler.store_urls(urls, status_code=State.URL_STORED.value, state=State.URL_STORED.value)
        key = URLHandler.update_state(url, status_code, state)
        response = queue.notify_ready()
        return '', 200


@crawler.route('/StoreHTML', methods=['POST', 'GET'])
def store_html():
    """ run start crawling
        usually this method called once
        if you call this method once again , it may happen something like crawler shut down
    """
    print('==========STORE_HTML===========')
    # if request.method == "POST":
    # token = request.form.get('token')
    print request.form
    filename = request.form.get('key')
    filestream = request.form.get('html')
    bucket_name = request.form.get('bucket_name')
    # fullpath = os.path.join(bucket_name,filename + '.gz')
    # keys = uploader.upload_to_gcs(fullpath, filestream)
    # url = uploader.upload_file(bucket_name, filename + '.gz', filestream)
    # queue.parse_page(fullpath)
    # handler.manager.update_state(urls,status_code,State.URL_STORED)
    # print url

    # return url, 200
    return '', 200


@crawler.route('/StoreHTML2', methods=['POST', 'GET'])
def store_html2():
    """ run start crawling
        usually this method called once
        if you call this method once again , it may happen something like crawler shut down
    """
    print('==========STORE_HTML2===========')
    # if request.method == "POST":
    # token = request.form.get('token')
    print request.form
    filename = request.form.get('key')
    filestream = request.form.get('html')
    bucket_name = request.form.get('bucket_name')
    fullpath = '/' + bucket_name + '/' + filename + '.gz'
    print fullpath
    print type(fullpath)
    uploader.upload_to_gcs(str(fullpath), filestream)
    # url = uploader.upload_file(bucket_name, filename + '.gz', filestream)
    # queue.parse_page(fullpath)
    # handler.manager.update_state(urls,status_code,State.URL_STORED)

    return 'Files stored', 200


@crawler.route('/NotifyReady', methods=['POST'])
def notify_ready():
    print('==========NotifyReady===========')
    if request.method == "POST":
        # token = request.headers['token']
        res = notify_ready_()
        print res
        return '', 200
    print 'GET is unauthorized'


@crawler.route('/ParsePage', methods=['POST'])
def parse_page():
    print('==========START CRAWLING===========')
    if request.method == "POST":
        token = request.headers['token']
        path = request.json.get('path')
        parser = HTMLParse(path)
        parser.parse()

        return '', 200


@crawler.route('/PostURL', methods=['POST', 'GET'])
def post_url():
    url = request.form.get('url')
    print url
    url_handler = URLHandler(url)
    print url_handler
    keys = url_handler.store_urls(url, 0, 0)
    print keys
    return 'key : {}  url : {}'.format(url_handler.generate_key(url), url), 200


@crawler.route('/quit', methods=['POST', 'GET'])
def quit():
    """ run start crawling
        usually this method called once
        if you call this method once again , it may happen something like crawler shut down
    """
    print('==========WIll Quite===========')
    manager = QuiteManager()
    key = manager.quite()
    # if request.method == "POST":
    print key
    print '========will quite soon========'
    return '', 200


@crawler.route('/create_quit', methods=['POST', 'GET'])
def create_quit():
    """ run start crawling
        usually this method called once
        if you call this method once again , it may happen something like crawler shut down
    """
    print('==========create Quite===========')
    q = QuiteManager(id='quite', state=False, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
    key = q.put()

    print key
    print '========created quite========'
    return '', 200


@crawler.route('/get_env', methods=['POST', 'GET'])
def get_env():
    """ run start crawling
        usually this method called once
        if you call this method once again , it may happen something like crawler shut down
    """
    print('==========get_env===========')
    import os
    print os.environ
    return str(os.environ.get('MANAGER_URL', '')), 200
