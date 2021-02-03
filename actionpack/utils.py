from itertools import chain


def tally(num=1):
    while (num if num > 0 else -1 * num) > 0:
        yield 1 if num > 0 else -1
        num = num - 1 if num > 0 else num + 1

