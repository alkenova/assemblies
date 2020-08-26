from collections import namedtuple
from types import MappingProxyType
from typing import Mapping, Tuple, List


class Recording:
    """
    A recording function, supports storing functions to replay later with additional parameters
    """

    Entry = namedtuple('Entry', ['function', 'positional_arguments', 'keyword_arguments'])

    def __init__(self):
        """
        Create a recording object
        """
        self.actions: List[Recording.Entry] = []

    def play(self, **kwargs):
        """Play a recording with additional keyword-arguments"""

        for function, positional_arguments, keyword_arguments in self.actions:
            effective_kwargs = {**keyword_arguments, **{k: v for k, v in kwargs.items() if k not in keyword_arguments}}
            function(*positional_arguments, **effective_kwargs)

    def append(self, func, positional_arguments: Tuple, keyword_arguments: Mapping):
        """Append a function to the recorded functions"""
        self.actions.append(Recording.Entry(func, positional_arguments, MappingProxyType(keyword_arguments)))
