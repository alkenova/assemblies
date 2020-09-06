from abc import ABCMeta

from assembly_calculus.learning.data_set.mask import Mask
from assembly_calculus.learning.data_set.lib.basic_types.data_set_base import DataSetBase


class PartialDataSet(DataSetBase, metaclass=ABCMeta):
    """
    A base class for training and test masks, applying a mask over a given
    data set to create a partial data set.
    """
    def __init__(self, base_data_set: DataSetBase, mask: Mask,
                 noise_probability: float = 0.) -> None:
        super().__init__(noise_probability)
        self._base_data_set = base_data_set
        self._mask = mask

    def __iter__(self):
        self.reset()
        self._base_data_set.reset()
        return self

    @property
    def input_size(self):
        return self._base_data_set.input_size
