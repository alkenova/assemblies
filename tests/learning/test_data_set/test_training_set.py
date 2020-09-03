from unittest import TestCase

from assembly_calculus.learning.components.data_set.constructors import create_explicit_mask_from_list, create_training_set_from_callable, \
    create_training_set_from_dict
from assembly_calculus.learning.components.data_set.data_point import DataPoint


class TestTrainingSet(TestCase):
    def test_training_set_returns_data_points(self):
        mask = create_explicit_mask_from_list([0, 0, 1, 1, 0, 1, 1, 1])
        s = create_training_set_from_callable(lambda x: x % 2, 3, mask, 100, 0.2)
        for data_point in s:
            self.assertIsInstance(data_point, DataPoint)

    def test_training_set_is_reusable(self):
        mask = create_explicit_mask_from_list([0, 0, 1, 1, 0, 1, 1, 1])
        s = create_training_set_from_callable(lambda x: x % 2, 3, mask, 100, 0.2)
        for data_point in s:
            self.assertIsInstance(data_point, DataPoint)

        # reuse
        reused = 0
        for data_point in s:
            reused += 1
            self.assertIsInstance(data_point, DataPoint)
        self.assertEqual(100, reused)

    def test_training_set_length_is_correct(self):
        mask = create_explicit_mask_from_list([0, 0, 1, 1, 0, 1, 1, 1])
        s = create_training_set_from_callable(lambda x: x % 2, 3, mask, 100, 0.2)
        self.assertEqual(100, len([i for i in s]))

    def test_training_set_has_noise(self):
        def func(x):
            return x % 2

        mask = create_explicit_mask_from_list([0, 0, 1, 1, 0, 1, 1, 1])
        s = create_training_set_from_callable(func, 3, mask, 100, 0.5)
        count_noisy = sum(data_point.output != func(data_point.input)
                          for data_point in s)

        self.assertGreater(100, count_noisy)
        self.assertLess(0, count_noisy)

    def test_training_set_has_absolute_noise(self):
        def func(x):
            return x % 2

        mask = create_explicit_mask_from_list([0, 0, 1, 1, 0, 1, 1, 1])
        s = create_training_set_from_callable(func, 3, mask, 100, 1)
        count_noisy = sum(data_point.output != func(data_point.input)
                          for data_point in s)

        self.assertEqual(100, count_noisy)

    def test_training_set_is_not_ordered(self):
        mask = create_explicit_mask_from_list([0, 0, 1, 1, 0, 1, 1, 1])
        s = create_training_set_from_callable(lambda x: x % 2, 3, mask, 8, 0.2)
        self.assertNotEqual(list(range(8)), [data_point.input for data_point in s])

    def test_training_set_is_partial(self):
        mask = create_explicit_mask_from_list([0, 0, 1, 1, 0, 1, 1, 1])
        s = create_training_set_from_callable(lambda x: x % 2, 3, mask, 1000, 0.2)
        indices = {data_point.input for data_point in s}
        self.assertNotIn(0, indices)
        self.assertNotIn(1, indices)
        self.assertNotIn(4, indices)

    def test_create_training_set_from_dict(self):
        data_set_dict = {1: 0, 3: 1, 5: 1}
        test_set = create_training_set_from_dict(data_set_dict, 4, 6)
        data_points = [(data_point.input, data_point.output)
                       for data_point in test_set]

        self.assertEqual(6, len(data_points))
        self.assertEqual([(1, 0), (1, 0), (3, 1), (3, 1), (5, 1), (5, 1)],
                         sorted(data_points))

    def test_create_training_set_from_dict_with_absolute_noise(self):
        data_set_dict = {1: 0, 3: 1, 5: 1}
        test_set = create_training_set_from_dict(data_set_dict, 4, 6, 1.)
        data_points = [(data_point.input, data_point.output)
                       for data_point in test_set]

        self.assertEqual(6, len(data_points))
        self.assertEqual([(1, 1), (1, 1), (3, 0), (3, 0), (5, 0), (5, 0)],
                         sorted(data_points))

