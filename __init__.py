#!/usr/bin/env python
"""
__init__.py - Phenny Init Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import sys, os, time, threading, signal
import bot

class Watcher(object):
    # Cf. http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496735
    def __init__(self):
        self._configs = []
        self._children = []
        signal.signal(signal.SIGTERM, self.sig_term)

    def add(self, config):
        self._configs.append(config)

    def _start(self, config):
        child = os.fork()
        if child != 0:
            self._children.append(child)
        else:
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            run_phenny(config)

    def run(self):
        for config in self._configs:
            self._start(config)

    def watch(self):
        alive = True
        while alive:
            self.run()

            try:
                proc = None
                while proc not in self._children:
                    (proc, _) = os.wait()
            except KeyboardInterrupt:
                alive = False

            self.kill()
        sys.exit()

    def kill(self):
        for child in self._children:
            try: os.kill(child, signal.SIGKILL)
            except OSError: pass
        self._children = []

    def sig_term(self, signum, frame):
        self.kill()
        sys.exit()

def run_phenny(config):
    if hasattr(config, 'delay'):
        delay = config.delay
    else: delay = 20

    def connect(config):
        p = bot.Phenny(config)
        p.run(config.host, config.port, config.ssl)

    while True:
        try: connect(config)
        except KeyboardInterrupt, e:
            raise e

        if not isinstance(delay, int):
            break

        warning = 'Warning: Disconnected. Reconnecting in %s seconds...' % delay
        print >> sys.stderr, warning
        time.sleep(delay)


def run(configs):
    w = Watcher()
    for config in configs:
        w.add(config)
    w.watch()

if __name__ == '__main__':
    print __doc__
