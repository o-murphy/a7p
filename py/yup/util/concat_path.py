__all__ = ('concat_path',)


def concat_path(path, item):
    # return path + "[%r]" % item
    if isinstance(item, str):
        if path == "":
            return item
        return ".".join((path, item))
    elif isinstance(item, int):
        return path + "[%r]" % item
    else:
        raise TypeError("Unsupported item type")
