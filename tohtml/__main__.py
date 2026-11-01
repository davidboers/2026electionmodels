import sys

from tohtml._tohtml import notebook_to_html

if __name__ == '__main__':
    args = sys.argv[1:]
    notebook_to_html(args[0], args[1])