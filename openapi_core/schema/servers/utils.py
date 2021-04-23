def is_absolute(url):
    return url.startswith('//') or '://' in url
