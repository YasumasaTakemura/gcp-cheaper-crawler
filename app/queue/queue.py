# -*- coding: utf-8 -*-
from google.appengine.api import taskqueue


# def pull_url():
#     task = taskqueue.add(
#         queue_name='PullURL',
#         url='/PullURL',
#         target='worker'
#     )
#     return task


def notify_ready():
    task = taskqueue.add(
        queue_name='NotifyReady',
        url='/NotifyReady',
        # target='default'
    )
    return task


def store_url(url,urls, status_code, state):
    task = taskqueue.add(
        queue_name='StoreURL',
        url='/StoreURL',
        target='worker',
        params={
            'url': url,
            'urls': urls,
            'status_code': status_code,
            'state': state,
        })
    return task


def store_html(html, bucket_name,key):
    print key
    print len(html)
    task = taskqueue.add(
        queue_name='StoreHTML',
        url='/StoreHTML2',
        target='worker',
        params={
            'html': html,
            'bucket_name': bucket_name,
            'key': key,

        })
    print task
    return task


def request_page(url):
    # data is url
    task = taskqueue.add(
        queue_name='RequestPage',
        url='/RequestPage',
        target='worker',
        params={'url': url})
    return task


def parse_page(path):
    # data is url
    task = taskqueue.add(
        queue_name='ParsePage',
        url='/ParsePage',
        target='worker',
        params={'path': path})
    return task

# def quitCrawling(url):
#     # data is url
#     task = taskqueue.add(
#         queue_name='quit',
#         url='/RequestURL',
#         target='worker',
#         params={'data': url})
#     return task
