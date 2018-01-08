# -*- coding: utf-8 -*-
import time
import re
import datetime
from bs4 import BeautifulSoup
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from app.crawler.exceptions import RetryError
from app.crawler.constants import State
import hashlib
import urlparse
import configparser
import yaml
import os

def modify_config(param):
    if param is None:
        return


def notify_ready():
    host = os.environ.get('MANAGER_URL','http://localhost:8080')
    host = 'http://localhost:8080'
    print '=============MANAGER_URL==============='
    print host
    print urlparse.urljoin(host, 'PullUrls')
    response = urlfetch.fetch(
        url=urlparse.urljoin(host, 'PullUrls'),
        method=urlfetch.POST
    )
    return response


def read_setting(path, kwd):
    with open(path, 'r') as f:
        setting = yaml.load(f)[kwd]
        return setting


class QuiteManager(ndb.Expando):
    state = ndb.BooleanProperty()
    created_at = ndb.DateTimeProperty()
    updated_at = ndb.DateTimeProperty()

    @classmethod
    def is_quiting(cls):
        return ndb.Key(cls, 'quite').get().state

    @classmethod
    def quite(cls):
        entity = ndb.Key(cls, 'quite').get()
        entity.state = True
        entity.updated_at = datetime.datetime.now()
        key = entity.put()
        return key


class URLHandlerModel(ndb.Expando):
    state = ndb.IntegerProperty()
    status_code = ndb.IntegerProperty()
    created_at = ndb.DateTimeProperty()
    updated_at = ndb.DateTimeProperty()

    @classmethod
    def is_duplicated(cls, key):
        if ndb.Key(cls, key).get():
            return True
        return False


class URLHandler(URLHandlerModel):
    def __init__(self, url=None):
        super(URLHandlerModel, self).__init__()
        self.url = url
        self.entities = []
        self.limit = 100

    def pull_urls(self):
        try:
            q = URLHandlerModel.query()
            self.entities = q.filter(URLHandler.state == 0).order(URLHandler.created_at).fetch(self.limit)
            return self.status
        except Exception as e:
            print e
            raise ValueError('None is returned')

    @classmethod
    def update_state(cls, url, status_code, state):
        # (string[list],string,string) -> ndb.Key()
        key = cls.generate_key(url)
        entity = ndb.Key(URLHandlerModel, key).get()
        print '======exist?======'
        print entity
        entity.status_code = int(status_code)
        entity.state = int(state)
        entity.updated_at = datetime.datetime.now()
        key = entity.put()
        return key

    @staticmethod
    def generate_key(url):
        return str("url-" + hashlib.sha256(url).hexdigest())[::-1]

    @classmethod
    def get_first_one(cls):
        try:
            q = cls.query()
            entity = q.filter(cls.state == 0).order(cls.created_at).get()
            return entity
        except Exception as e:
            print e
            raise ValueError('None is returned')

    @classmethod
    def store_urls(cls, urls, status_code, state):
        print '-----store_urls-----'
        urls_to_store = []
        if isinstance(urls, (str, unicode)):
            urls = [urls]
        for _url in urls:
            # reverse keys to distribute each entities
            _key = cls.generate_key(_url)
            if URLHandlerModel.is_duplicated(_key):
                continue
                # state = State.URL_DUPLICATED.value
            entity = URLHandlerModel(
                id=_key,
                url=_url,
                state=state,
                status_code=status_code,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now()
            )
            urls_to_store.append(entity)
        _keys = ndb.put_multi(urls_to_store)
        return _keys


class RequestHandler(object):
    def __init__(self, url):
        self._retry = 3
        self._interval = 4
        self.UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36'
        self.header = {
            'User-Agent': self.UA
        }
        self.url = url
        self.manager = URLHandler(url)
        self.domain = self.get_hostname()
        self.quit = False

    # def __repr__(self):
    #     return '<{}>'.format(self.__class__.__name__)

    def is_alive(self):
        return True

    def get_hostname(self):
        result = urlparse.urlsplit(self.url)
        domain = result.scheme + "://" + result.netloc
        return domain

    def extract_url(self, html):
        urls = []
        html = BeautifulSoup(html, 'html.parser')
        for link in html.find_all("a"):
            url = link.get("href")
            # todo: not efficient to call instance in a loop
            valid_url = URLValidator(url).validate()
            if valid_url:
                urls.append(valid_url)
        return urls

    def wait(self, interval=None):
        interval = interval if interval else self._interval
        time.sleep(interval)

    def get_page(self, url=None):
        url = url if url else self.url
        while self._retry > 0:
            try:
                res = urlfetch.fetch(url=url, headers=self.header)
                return StatusHandler(res, url)
            except Exception as e:
                print e
                self._retry -= 1
                self.wait()
        raise RetryError("retried {} but did not make it.".format(self._retry))


class StatusHandler:
    def __init__(self, res, url):
        self.status_code = res.status_code
        self.state = self._check()
        self.headers = res.headers
        self.url = url
        self.path = ''
        self.body = None if self.status_code in (State.NOT_EXISTED, State.RESUMING) else res.content

    def _check(self):
        if 400 <= self.status_code < 500:
            return State.NOT_EXISTED
        elif self.status_code >= 500:
            return State.RESUMING
        else:
            return State.CRAWLED


class URLValidator:
    re_startswith_slash = re.compile(r'(^/[\w.-]+)')
    DisallowedURLs = read_setting('setting.yaml', 'DisallowedURLs')

    def __init__(self, url):
        self.url = url

    def __call__(self, *args, **kwargs):
        return self.validate()

    def validate(self):
        if self._is_valid_url() and self._is_allowed():
            return self.url

    def _is_allowed(self):
        for url in self.DisallowedURLs:
            if not re.match(r'{}'.format(url), self.url):
                return True
        return False

    def _is_valid_url(self):
        if self.url and self.re_startswith_slash.match(self.url) and self.url.find('AppPage') == -1:
            return True
        return False
