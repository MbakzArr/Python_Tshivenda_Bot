import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
USER_DIR = os.path.join(ROOT, "userdata")


def data(name):
    return os.path.join(DATA_DIR, name)


def user(name):
    if not os.path.isdir(USER_DIR):
        os.makedirs(USER_DIR)
    return os.path.join(USER_DIR, name)
