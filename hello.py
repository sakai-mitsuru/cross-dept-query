##
# cmd prompt using
# chcp 65001
#   set PYTHONIOENCODING=utf-8
#
import sys

def hello():
    print("Encoding is ", sys.stdin.encoding)
    print('Hello python!  モモチ');

if __name__ == '__main__' :
    hello();
