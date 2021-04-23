import sys


class Spec(object):
    sep = '/'

    def __new__(cls, *args):
        return cls._from_parts(args)

    @classmethod
    def _parse_args(cls, args):
        # This is useful when you don't want to create an instance, just
        # canonicalize some constructor arguments.
        parts = []
        for a in args:
            if isinstance(a, Spec):
                parts += a._parts
            else:
                if isinstance(a, str):
                    # Force-cast str subclasses to str (issue #21127)
                    parts.append(str(a))
                else:
                    raise TypeError(
                        "argument should be a str object or a Spec "
                        "object returning str, not %r"
                        % type(a))
        return cls.parse_parts(parts)

    @classmethod
    def parse_parts(cls, parts):
        parsed = []
        sep = cls.sep
        root = ''
        it = reversed(parts)
        for part in it:
            if not part:
                continue
            root, rel = cls.splitroot(part)
            if sep in rel:
                for x in reversed(rel.split(sep)):
                    if x and x != '.':
                        parsed.append(sys.intern(x))
            else:
                if rel and rel != '.':
                    parsed.append(sys.intern(rel))
        parsed.reverse()
        return root, parsed

    @classmethod
    def splitroot(cls, part, sep=sep):
        if part and part[0] == sep:
            stripped_part = part.lstrip(sep)
            # According to POSIX path resolution:
            # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap04.html#tag_04_11
            # "A pathname that begins with two successive slashes may be
            # interpreted in an implementation-defined manner, although more
            # than two leading slashes shall be treated as a single slash".
            if len(part) - len(stripped_part) == 2:
                return sep * 2, stripped_part
            else:
                return sep, stripped_part
        else:
            return '', part

    @classmethod
    def _from_parts(cls, args):
        self = object.__new__(cls)
        root, parts = cls._parse_args(args)
        self._root = root
        self._parts = parts
        return self

    @classmethod
    def _from_parsed_parts(cls, root, parts):
        self = object.__new__(cls)
        self._root = root
        self._parts = parts
        return self

    def join_parsed_parts(self, root, parts, root2, parts2):
        """
        Join the two paths represented by the respective
        (root, parts) tuples.  Return a new (root, parts) tuple.
        """
        if root2:
            return root2, root2 + parts2[1:]
        elif parts:
            return root, parts + parts2
        return root2, parts2

    def _make_child(self, args):
        root, parts = self._parse_args(args)
        root, parts = self.join_parsed_parts(
            self._root, self._parts, root, parts)
        return self._from_parsed_parts(root, parts)

    def __truediv__(self, key):
        return self._make_child((key,))
