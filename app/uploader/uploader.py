# -*- coding: utf-8 -*-
import cloudstorage as cs
import zlib
from app.tasklet import tasklet

cs.set_default_retry_params(
    cs.RetryParams(
        initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15
    ))

def gcs_path_generator(bucket_name, filename, ext='gz'):
    bucket_name = tasklet.strip_slash(bucket_name)
    filename = tasklet.strip_slash(filename)
    fullpath = '/' + bucket_name + '/' + filename + '.' + ext
    return fullpath


def upload_to_gcs(path, data):
    try:
        with cs.open(path, 'w', content_type='application/gzip') as gcsf:
            gcsf.write(zlib.compress(data, 9))
        return gcsf.closed
    except Exception as e:
        print e
