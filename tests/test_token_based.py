import unittest
import numpy as np
from wafamole.models import TokenClassifierWrapper


class TokenClassifierTest(unittest.TestCase):
    def test_extract_features_ok(self):
        class test_object:
            def predict_proba():
                pass

            def fit():
                pass

        clf = TokenClassifierWrapper(test_object())
        query = "select * from a"
        expected = np.array([0, 2, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0])
        actual = clf.extract_features(query)
        self.assertTrue((actual == expected).all())

    def test_extract_features_no_str_throws_exception(self):
        class test_object:
            def predict_proba():
                pass

            def fit():
                pass

        clf = TokenClassifierWrapper(test_object())
        self.assertRaises(TypeError, clf.extract_features, 21)
