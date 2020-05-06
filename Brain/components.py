import math
from typing import List, Union


class Stimulus:
    # Beta may be static
    def __init__(self, n: int, beta: float):
        self.n = n
        self.beta = beta

    def __repr__(self):
        return f"Stimulus{(self.n, self.beta)}"


class Area:
    def __init__(self, n: int, k: int, beta: float=0.01):
        self.beta: float = beta
        self.n: int = n
        self.k: int = k
        self.support: List[int] = [0] * self.n
        self.winners: List[int] = []
        self.new_winners: List[int] = []

        if k < 0:
            self.k = math.sqrt(n)

    def __repr__(self):
        return f"Area{(self.n, self.k, self.beta)}"


class Connection:
    def __init__(self, source, dest, synapses=None):
        self.source = source
        self.dest = dest
        self.synapses = synapses

    @property
    def beta(self):
        if isinstance(self.source, Stimulus):
            return self.dest.beta
        return self.source.beta

    def __getitem__(self, key):
        return self.synapses[key]

    def __setitem__(self, key, value):
        self.synapses[key] = value

    def __repr__(self):
        return f"Connection({self.synapses!r})"


BrainPart = Union[Area, Stimulus]

__all__ = ['BrainPart', 'Connection', 'Stimulus', 'Area']