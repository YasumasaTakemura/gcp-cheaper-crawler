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

# @app.route('/')
# def hello():
#     print('========== start connection ===========')
#     # s = Store()
#     # b = s.list_bucket('/tests-tv-crawler')
#     # s.create_file('/tests-tv-crawler2/tests.txt')
#     # s.create_file('/tests-tv-crawler/test_{}.log'.format(datetime.datetime.now()))
#     # s.log()
#     # # print logs
#     # # print(s.format_log_entry(logs))
#     return '<html><header><title>index</title></header><body><h1>here is index</h1></body></html>'
#
#
# @app.route('/tests')
# def tests():
#     store = StoreExpado(
#         # _key_name='__id001',
#         id='__id001',
#         title='Crazy like a diamond',
#         author='Lucy Sky',
#         publish_date='yesterday',
#         rating=5.0,
#         created=datetime.datetime.now()
#
#     )
#     store.put()
#     return '<h3> tests </h3>'
#
#
# @app.route('/get')
# def get():
#     store = StoreExpado().get_by_id('__id001').title
#     # store.put()
#     return '<h3> {} </h3>'.format(store)
#
#
# @app.route('/add/<string:endpoint>/<string:msg>')
# def add_queue(endpoint, msg):
#     print('========== enqueue ===========')
#     s = Store()
#     s.add_queue(endpoint, msg)
#     s.log()
#     return '<h1>enqueued you task</h1>'
#
#
# # @app.route('/stream_insert/<string:data>')
# # def stream_data(data):
# #     print('========== stream_data ===========')
# #     s = Store()
# #     # cached = s.stream_insert(dataset_name=dataset,table_name=table,json_data=s.to_json(**{"name":data}))
# #     res = s.stream_insert(data)
# #     print(res)
# #     s.log()
#
#     # return '<h1>stream_data {}</h1>'.format("successed")
#
# @app.route('/get_cached/<string:key>')
# def get_cached(key):
#     print('========== cached ===========')
#     s = Store()
#     cached = s.get_mem(key)
#     s.log()
#     return '<h1>your cache is {}</h1>'.format(cached)
#
#
# @app.route('/add_cached/<string:key>/<string:value>')
# def add_cached(key, value):
#     print('========== cached ===========')
#     s = Store()
#     s.add_mem(key, value)
#     s.log()
#     return '<h1>cached your task</h1>'
#
# @app.route('/set_cached/<string:key>/<string:value>')
# def set_cached(key, value):
#     print('========== set cached ===========')
#     s = Store()
#     s.add_mem(key, value)
#     s.log()
#     return '<h1>set cache on your task \n key is {} value is {}</h1>'.format(key, value)
#
#
# @app.route('/push_to_gcs', methods=['POST', 'GET'])
# def push_to_gcs():
#     print('========== push_to_gcs ===========')
#     if request.method == 'POST':
#         msg = request.form['msg']
#         s = Store()
#         s.push_to_gcs('/tests-tv-crawler/test_{}.log'.format(datetime.datetime.now()), msg)
#         s.log()
#     return '<h1>enqueued you task!!!</h1> '
#
#
# @app.route('/q', methods=['POST', 'GET'])
# def queue():
#     print('==========  msg ===========')
#     if request.method == 'POST':
#         msg = request.form['msg']
#     print(msg)
#     return msg
#
#
# @app.route('/calc', methods=['POST', 'GET'])
# def calc():
#     print('==========  calc ===========')
#     # counter = 0
#     # primes = [2, 3]
#     #
#     # for n in range(5, 10001, 2):
#     #     isprime = True
#     #     for i in range(1, len(primes)):
#     #         counter += 1
#     #         if primes[i] ** 2 > n:
#     #             break
#     #         counter += 1
#     #         if n % primes[i] == 0:
#     #             isprime = False
#     #             break
#     #     if isprime:
#     #         primes.append(n)
#     # print primes, len(primes)
#     # return str(len(primes))
#     return '==========  calc is done ==========='