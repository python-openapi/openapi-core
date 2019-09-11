import attr


@attr.s(hash=True)
class Contribution(object):
    src_prop_name = attr.ib()
    src_prop_attr = attr.ib(default=None)
    dest_prop_name = attr.ib(default=None)
    is_list = attr.ib(default=False)
    is_dict = attr.ib(default=False)
    dest_default = attr.ib(default=None)
