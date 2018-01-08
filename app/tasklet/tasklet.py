import urlparse

def strip_slash(word):
    if word.startswith('/'):
        word = word[1:]
    if word.endswith('/'):
        word = word[:-1]
    return word


def join_url(domain=None, *args):
    url_joined = []

    if not domain:
        for path in args:
            url_joined.append(path)
        url = '/'.join(url_joined)[1:]
        return url
    for path in args:
        if path.find(domain) != -1:
            path = path.replace(domain, '')
        if not path:
            continue
        path = strip_slash(path)
        url_joined.append(path)
    path = '/'.join(url_joined)
    return urlparse.urljoin(domain, path)