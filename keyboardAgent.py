#!/usr/bin/env python
# encoding: utf-8


class PlayerAgent(object):

    def __init__(self):
        pass

    def get_action(self, state):
        "return a legal action according to the state"


class _Getch(object):
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()
    def __call__(self):
        return self.impl()


class _GetchUnix(object):
    def __init__(self):
        import sys, tty, termios
    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows(object):
    def __init__(self):
        import msvcrt
        self.getch = msvcrt.getch
    def __call__(self):
        return self.getch()


getch = _Getch()


if __name__ == '__main__':
    print 'Example use of `getch` function.  Use Control-C to exit'
    import sys
    while 1:
        c = getch()
        if c == '':
            print
            raise SystemExit
        try:
            c.decode('ascii')
        except UnicodeDecodeError:
            pass
        else:
            sys.stdout.write(c)

