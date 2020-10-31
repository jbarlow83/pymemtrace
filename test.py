import sys

import psutil

import custom
import cPyMemTrace


def f(l):
    print('Hi')
    s = ' ' * l
    print('Bye')


def g():
    print(f'Creating Custom.')
    # pid = psutil.Process()
    # print(f'Creating Custom: {pid.memory_info()}')
    obj = custom.Custom('First', 'Last')
    print(obj.name())
    # print(f'Done: {pid.memory_info()}')
    print(f'Done.')


def main():
    cPyMemTrace.attach_profile()
    f(1024**2)
    # f(1024**2)
    g()
    cPyMemTrace.detach_profile()
    return 0


if __name__ == '__main__':
    sys.exit(main())
