def test(b):
    def foo(a):
        return a * 10
    return foo(b)


def foo(b):
    def test(a):
        return a * 5
    return test(b)


def main():
    print(test(5))
    print(foo(5))


if __name__ == "__main__":
    main()
