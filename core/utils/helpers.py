from time import sleep
from random import randrange
# =========================
# General helpers
# =========================
def wait(delay, jitter):
    if jitter == 0:
        sleep(delay)
    else:
        sleep(delay + randrange(jitter))


# =========================
# Data manipulation helpers
# =========================
def loop_dict(dict_):
    for key in dict_.keys():
        yield key


def get_list_from_file(file_):
    with open(file_, "r") as f:
        list_ = [line.strip() for line in f]
    return list_


# =========================
# Password spraying helpers
# =========================
def lockout_reset_wait(lockout):
    print("[*] Sleeping for %.1f minutes" % (lockout))
    sleep(lockout * 60)