import os

from .index import Mosflm_index
from .strategy import Mosflm_strategy
from .integrate import Mosflm_integrate

class mosflm_factory:

    def __init__(self):
        self._working_directory = os.getcwd()
        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        return

    def index(self):
        _index = Mosflm_index()
        _index.set_working_directory(self._working_directory)
        return _index

    def strategy(self):
        _strategy = Mosflm_strategy()
        _strategy.set_working_directory(self._working_directory)
        return _strategy

    def integrate(self):
        _integrate = Mosflm_integrate()
        _integrate.set_working_directory(self._working_directory)
        return _integrate
