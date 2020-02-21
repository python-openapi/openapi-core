from parse import Parser


def search(path_pattern, full_url_pattern):
    p = Parser(path_pattern)
    p._expression = p._expression + '$'
    return p.search(full_url_pattern)


def parse(server_url, server_url_pattern):
    p = Parser(server_url)
    p._expression = '^' + p._expression
    return p.parse(server_url_pattern)
