import sys
from troll.main import run


def main():
    run(" ".join(sys.argv[1:]))


if __name__ == '__main__':
    main()
