#!/usr/bin/env python
# InteractiveDriver.py
#
#   Copyright (C) 2006 CCLRC, Graeme Winter
#
#   This code is distributed under the BSD license, a copy of which is
#   included in the root directory of this package.
#
# 24th May 2006
#
# An implementation based on the simplest Driver type - the one which
# just wraps the subprocess.Popen class. Note well: this will require
# Python 2.4. However, this adds timeouts and job control to the mix -
# a better use of the interactive interface.
#
# Applicability: Windows/OS X/UNIX
#

import subprocess

from DefaultDriver import DefaultDriver
from DriverHelper import kill_process

class InteractiveDriver(DefaultDriver):

    def __init__(self):
        DefaultDriver.__init__(self)

        self._popen = None

        return

    def start(self):
        if self._executable is None:
            raise RuntimeError, 'no executable is set.'

        command_line = []
        command_line.append(self._executable)
        for c in self._command_line:
            command_line.append(c)

        self._popen = subprocess.Popen(command_line,
                                       bufsize = 1,
                                       stdin = subprocess.PIPE,
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.STDOUT,
                                       cwd = self._working_directory,
                                       universal_newlines = True,
                                       shell = True)

        # somehow here test for failure - oh, you can't because
        # the shell spawned is probably still ok

        # check here anyway - sometimes this failure can be trapped

        if not self.check():
            # do something useful here - need to look for signs that the
            # program has stopped unexpectedly not just been instant
            pass

        return

    def check(self):
        '''Overload the default check method.'''

        if self._popen.poll() is None:
            return True

        return False

    def _input(self, record):

        if not self.check():
            raise RuntimeError, 'child process has termimated'

        self._popen.stdin.write(record)

        return

    def _output(self):
        # need to put some kind of timeout facility on this...
        # in particular for the interactive version

        # 31/MAY/06
        # oh - looks like there isn't a portable way of doing this -
        # select does not work with file descriptors on Windows
        return self._popen.stdout.readline()

    def _status(self):
        # get the return status of the process

        return self._popen.poll()

    def close(self):
        if not self.check():
            raise RuntimeError, 'child process has termimated'

        self._popen.stdin.close()

        return

    def kill(self):
        kill_process(self._popen)

        return

if __name__ == '__main__':
    # run a test for segmentation fault

    d = InteractiveDriver()

    d.set_executable('EPSegv')
    d.start()
    d.close()
    while True:
        line = d.output()
        if not line:
            break

    d.check_for_errors()
