import os

from .strategy import BestStrategy

class embl_factory:

    def __init__(self):
        self._working_directory = os.getcwd()
        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        return

    def strategy(self):
        _strategy = BestStrategy()
        _strategy.set_working_directory(self._working_directory)
        return _strategy

