from unittest import TestCase

from assembly_calculus.learning.components.data_set.constructors import create_data_set_from_list
from assembly_calculus.learning.components.data_set.errors import DataSetSizeError, DataSetValueError


class TestListDataSet(TestCase):
    def test_data_set_with_list_of_2_works(self):
        s = create_data_set_from_list([1, 0])
        self.assertEqual(1, s.input_size)
        self.assertEqual(1, next(s).output)
        self.assertEqual(0, next(s).output)
        self.assertRaises(StopIteration, next, s)

    def test_data_set_with_list_of_3_fails(self):
        self.assertRaises(DataSetSizeError, create_data_set_from_list,
                          [1, 0, 1])

    def test_data_set_with_non_boolean_values_fails(self):
        s = create_data_set_from_list([1, 3])
        self.assertEqual(1, next(s).output)
        self.assertRaises(DataSetValueError, next, s)

    def test_data_set_with_list_of_16_works(self):
        expected = [
            1, 0, 1, 0,
            1, 1, 1, 1,
            0, 0, 0, 0,
            1, 0, 1, 0
        ]
        s = create_data_set_from_list(expected)
        self.assertEqual(4, s.input_size)
        for expected_value in expected:
            self.assertEqual(expected_value, next(s).output)
        self.assertRaises(StopIteration, next, s)

    def test_data_set_iterable_works(self):
        expected = [
            1, 0, 1, 0,
            1, 1, 1, 1,
            0, 0, 0, 0,
            1, 0, 1, 0
        ]
        s = create_data_set_from_list(expected)
        for i, data_point in enumerate(s):
            self.assertEqual(expected[i], data_point.output)

    def test_data_set_is_reusable(self):
        expected = [
            1, 0, 1, 0,
            1, 1, 1, 1,
            0, 0, 0, 0,
            1, 0, 1, 0
        ]
        s = create_data_set_from_list(expected)
        for i, data_point in enumerate(s):
            self.assertEqual(expected[i], data_point.output)

        # reuse
        reused = 0
        for i, data_point in enumerate(s):
            reused += 1
            self.assertEqual(expected[i], data_point.output)
        self.assertEqual(2 ** s.input_size, reused)

    def test_data_set_with_full_noise_flips_all_results(self):
        expected_not_noisy = [
            1, 0, 1, 0,
            1, 1, 1, 1,
            0, 0, 0, 0,
            1, 0, 1, 0
        ]
        s = create_data_set_from_list(expected_not_noisy, noise_probability=1)
        for i, data_point in enumerate(s):
            self.assertEqual(expected_not_noisy[i] ^ 1, data_point.output)

    def test_data_set_with_noise_flips_some_results(self):
        expected_not_noisy = [
            1, 0, 1, 0,
            1, 1, 1, 1,
            0, 0, 0, 0,
            1, 0, 1, 0
        ]
        s = create_data_set_from_list(expected_not_noisy, noise_probability=0.5)
        count_flipped = sum(expected_not_noisy[i] ^ data_point.output for i, data_point in enumerate(s))

        # Note: This test can fail with extremely low probability.
        #       If it does, run again to verify it was one of those extreme cases.
        self.assertLess(0, count_flipped)
        self.assertGreater(len(expected_not_noisy), count_flipped)
