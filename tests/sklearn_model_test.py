import unittest
import joblib
import os
import numpy as np
from wafamole.models import SklearnModelWrapper
from wafamole.exceptions.models_exceptions import (
    NotSklearnModelError,
    SklearnInternalError,
    ModelNotLoadedError
)


class SklearnWrapperTest(unittest.TestCase):
    def setUp(self):
        class test_object:
            def predict_proba(self):
                pass

            def fit(self):
                pass

        self.root_module_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.compliant_object = test_object()
        self.test_model_path = os.path.join(
            self.root_module_path, "tests/local_test_file/test_sklearn_model.dump"
        )
        self.test_sklearn_model = joblib.load(self.test_model_path)
        self.test_sample = np.zeros(12)
        self.test_X = np.zeros((20, 12))
        self.test_Y = np.ones(20)
        self.test_Y[: len(self.test_Y) // 2] = 0
        return super().setUp()

    def test_object_probability_no_decision_function_throws_exception(self):
        class wrong_object:
            def __init__(self):
                self.probability = True

            def predict_proba():
                pass

            def fit():
                pass

        self.assertRaises(NotSklearnModelError, SklearnModelWrapper, wrong_object())

    def test_object_probability_decision_function_ok(self):
        class test_object:
            def __init__(self):
                self.probability = True

            def predict_proba(self):
                pass

            def decision_function(self):
                pass

            def fit(self):
                pass

        _ = SklearnModelWrapper(test_object())
        self.assertTrue(True)

    def test_object_without_fit_throws_exception(self):
        class test_object:
            def fit(self):
                pass

        self.assertRaises(NotSklearnModelError, SklearnModelWrapper, test_object())

    def test_object_without_predict_proba_throws_exception(self):
        class test_object:
            def predict_proba(self):
                pass

        self.assertRaises(NotSklearnModelError, SklearnModelWrapper, test_object())

    def test_load_no_string_passed_throws_exception(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        self.assertRaises(TypeError, wrapper.load, 12)

    def test_load_no_regular_file_passed_throws_exception(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        self.assertRaises(FileNotFoundError, wrapper.load, "not exists")

    def test_load_no_regular_file_passed_throws_exception(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        self.assertRaises(
            NotSklearnModelError,
            wrapper.load,
            os.path.join(self.root_module_path, "README.md"),
        )

    def test_regular_model_load_ok(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        wrapper.load(self.test_model_path)
        self.assertTrue(True)

    def test_classify_no_array_throws_exception(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        self.assertRaises(TypeError, wrapper.classify, 12)

    def test_classify_invalid_input_throws_exception(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        self.assertRaises(SklearnInternalError, wrapper.classify, np.zeros(100))

    def test_classify_ok(self):
        wrapper = SklearnModelWrapper(self.test_sklearn_model)
        confidence = wrapper.classify(self.test_sample)
        self.assertTrue(True)

    def test_extract_features_no_array_throws_exception(self):
        wrapper = SklearnModelWrapper(self.test_sklearn_model)
        self.assertRaises(TypeError, wrapper.extract_features, 12)

    def test_extract_features_ok(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        feat_vector = wrapper.extract_features(self.test_sample)
        self.assertTrue((feat_vector == self.test_sample).all())

    def test_fit_no_X_array_throws_exception(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        self.assertRaises(TypeError, wrapper.fit, *[0, self.test_Y])

    def test_fit_no_Y_array_throws_exception(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        self.assertRaises(TypeError, wrapper.fit, *[self.test_X, 0])

    def test_fit_invalid_input_throws_exception(self):
        wrapper = SklearnModelWrapper(self.compliant_object)
        self.assertRaises(
            SklearnInternalError, wrapper.fit, *[self.test_X, np.zeros((100, 100))]
        )

    def test_fit_no_model_throws_exception(self):
        wrapper = SklearnModelWrapper()
        self.assertRaises(
            ModelNotLoadedError, wrapper.fit, *[self.test_X, np.zeros((100, 100))]
        )

    def test_fit_ok(self):
        wrapper = SklearnModelWrapper(self.test_sklearn_model)
        wrapper.fit(self.test_X, self.test_Y)
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
