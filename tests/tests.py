# -*- coding: utf-8 -*-
class A(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']


class B(A):
    def __init__(self, type):
        super(B, self).__init__(name='000')
        self.type = type


b = B(type='ppp')

import re
import yaml


def read_setting(path, kwd):
    with open(path, 'r') as f:
        setting = yaml.load(f)[kwd]
        return setting


class URLValidator:
    re_startswith_slash = re.compile(r'(^/[\w.-]+)')
    DisallowedURLs = read_setting('setting.yaml', 'DisallowedURLs')

    def __init__(self, url):
        self.url = url

    def __call__(self, *args, **kwargs):
        return self.check()

    def check(self):
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

import zlib
def decomp():
    print '--'
    with open('test2.gz','rb') as f:
        print f
        file = zlib.decompress(f.read())

    with open('test2.html','w') as f:
        f.write(file)
