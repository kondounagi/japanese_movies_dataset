import functools


def sort_by(sorter=None, uniq=False):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lst = list(func(*args, **kwargs))

            if uniq:
                lst = [dict(s) for s in set(tuple(e.items()) for e in lst)]

            return sorted(lst, key=sorter)
        return wrapper
    return deco
