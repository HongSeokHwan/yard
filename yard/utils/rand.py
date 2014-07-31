import os

from yard.utils.hash import get_hash_value


def random_hash():
    return get_hash_value(os.urandom(100))
