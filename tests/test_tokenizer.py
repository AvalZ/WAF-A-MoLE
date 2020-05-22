import os
import unittest
import numpy as np
from wafamole.tokenizer.tokenizer import Tokenizer


class TokenizerTest(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()
        self.root_module_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.model_dump_path = os.path.join(
            self.root_module_path, "tests/local_test_file/test_sklearn_model.dump"
        )
        self.file_test_dataset = os.path.join(
            self.root_module_path, "tests/local_test_file/test_dataset"
        )

    def test_produce_feat_vector_ok(self):
        query = "select * from a"
        expected = np.array([0, 2, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0])
        actual = self.tokenizer.produce_feat_vector(query)
        self.assertTrue((actual == expected).all())

    def test_produce_feat_vector_normalized_ok(self):
        query = "select * from a"
        expected = np.array([0, 2, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0])
        expected = expected / np.linalg.norm(expected)
        expected_norm = np.linalg.norm(expected)
        actual = self.tokenizer.produce_feat_vector(query, normalize=True)
        self.assertTrue((actual == expected).all())
        self.assertEqual(expected_norm, np.linalg.norm(actual))

    def test_produce_feat_vector_no_string_throws_exception(self):
        self.assertRaises(TypeError, self.tokenizer.produce_feat_vector, 12)

    def test_create_dataset_no_str_filepath_throws_exception(self):
        self.assertRaises(TypeError, self.tokenizer.create_dataset_from_file, *[12, 0])

    def test_create_dataset_no_regular_filepath_throws_exception(self):
        self.assertRaises(
            FileNotFoundError, self.tokenizer.create_dataset_from_file, *["12", 0]
        )

    def test_create_dataset_no_label_int_filepath_throws_exception(self):
        self.assertRaises(
            TypeError,
            self.tokenizer.create_dataset_from_file,
            *[self.model_dump_path, "hello"]
        )

    def test_create_dataset_no_bool_unique_rows_throws_exception(self):
        self.assertRaises(
            TypeError,
            self.tokenizer.create_dataset_from_file,
            *[self.model_dump_path, 1, 10, []]
        )

    def test_create_dataset_no_int_limit_throws_exception(self):
        self.assertRaises(
            TypeError,
            self.tokenizer.create_dataset_from_file,
            *[self.model_dump_path, 1, "limit"]
        )

    def test_create_dataset_no_limit_unique_rows_ok(self):
        actual_X, actual_y = self.tokenizer.create_dataset_from_file(
            self.file_test_dataset, 1, limit=None, unique_rows=True
        )
        expected_X = np.array(
            [[0, 3, 2, 0, 1, 0, 0, 1, 1, 0, 0, 0], [0, 3, 5, 0, 1, 2, 0, 1, 0, 0, 0, 0]]
        )
        expected_y = np.array([1, 1])
        self.assertTrue((actual_X == expected_X).all())
        self.assertTrue((actual_y == expected_y).all())

    def test_create_dataset_no_limit_no_unique_rows_ok(self):
        actual_X, actual_y = self.tokenizer.create_dataset_from_file(
            self.file_test_dataset, 1, limit=None, unique_rows=False
        )
        expected_X = np.array(
            [
                [0, 3, 2, 0, 1, 0, 0, 1, 1, 0, 0, 0],
                [0, 3, 2, 0, 1, 0, 0, 1, 1, 0, 0, 0],
                [0, 3, 5, 0, 1, 2, 0, 1, 0, 0, 0, 0],
            ]
        )
        expected_y = np.array([1, 1, 1])
        self.assertTrue((actual_X == expected_X).all())
        self.assertTrue((actual_y == expected_y).all())

    def test_create_dataset_limit_no_unique_rows_ok(self):
        actual_X, actual_y = self.tokenizer.create_dataset_from_file(
            self.file_test_dataset, 1, limit=1, unique_rows=False
        )
        expected_X = np.array([[0, 3, 2, 0, 1, 0, 0, 1, 1, 0, 0, 0]])
        expected_y = np.array([1])
        self.assertTrue((actual_X == expected_X).all())
        self.assertTrue((actual_y == expected_y).all())

    def test_get_allowed_tokens_ok(self):
        self.assertEqual(len(self.tokenizer.get_allowed_tokens()), 12)
