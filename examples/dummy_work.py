
def add(x,y):
    x+=str(y)
    return x


def add_2(x,y):
    if y % 20000 == 0:
        z=[]
        for q in range(0,400000):
            z.append(q)


def main():
    a=[]
    for n in range(0,200000):
        add(a,n)
        add_2(a,n)


def main_prof():
    main()


if __name__ == '__main__':
    main_prof()

