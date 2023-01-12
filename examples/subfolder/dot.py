import random


def dot(x, y):
    res = 0.0

    for n in range(len(x)):
        res += x[n] * y[n]

    return res


def populate(x, y):
    for n in range(len(x)):
        x[n] = random.random()
        y[n] = random.random()


def benchmark():
    size = 100
    x = [None] * size
    y = [None] * size
    populate(x, y)
    print(dot(x, y))


if __name__ == '__main__':
    benchmark()
