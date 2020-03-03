from base64 import urlsafe_b64decode


def b64decode(s):
    # Code from
    # https://github.com/GehirnInc/python-jwt/blob/master/jwt/utils.py#L29
    s_bin = s.encode('ascii')
    s_bin += b'=' * (4 - len(s_bin) % 4)
    return urlsafe_b64decode(s_bin)
