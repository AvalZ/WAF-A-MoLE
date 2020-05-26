import unittest
import keras
import numpy as np
import os
from wafamole.models import KerasModelWrapper
from wafamole.exceptions.models_exceptions import KerasInternalError, NotKerasModelError


class KerasWrapperTest(unittest.TestCase):
    """Keras wrapper test class"""

    def setUp(self):
        class test_object:
            def predict(self):
                pass

        self.compliant_object = test_object()
        self.root_module_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.test_model_path = os.path.join(
            self.root_module_path, "tests/local_test_file/test_keras_model.h5"
        )
        self.test_keras_model = keras.models.load_model(self.test_model_path)
        self.test_sample = np.zeros(20)
        self.test_X = np.random.randn(100, 20)
        self.test_Y = np.zeros(100)
        return super().setUp()


    def test_object_without_predict_throws_exception(self):
        class test_object:
            pass

        self.assertRaises(NotKerasModelError, KerasModelWrapper, test_object())

    def test_load_no_string_passed_throws_exception(self):
        wrapper = KerasModelWrapper(self.compliant_object)
        self.assertRaises(TypeError, wrapper.load, 12)

    def test_load_no_regular_file_passed_throws_not_exists_exception(self):
        wrapper = KerasModelWrapper(self.compliant_object)
        self.assertRaises(FileNotFoundError, wrapper.load, "not exists")

    def test_load_no_regular_file_passed_throws_exception(self):
        wrapper = KerasModelWrapper(self.compliant_object)
        self.assertRaises(
            NotKerasModelError,
            wrapper.load,
            os.path.join(self.root_module_path, "README.md"),
        )

    def test_regular_model_load_ok(self):
        wrapper = KerasModelWrapper(self.compliant_object)
        wrapper.load(self.test_model_path)
        self.assertTrue(True)

    def test_classify_no_array_throws_exception(self):
        wrapper = KerasModelWrapper(self.compliant_object)
        self.assertRaises(TypeError, wrapper.classify, 12)

    def test_classify_invalid_input_throws_exception(self):
        wrapper = KerasModelWrapper(self.compliant_object)
        self.assertRaises(KerasInternalError, wrapper.classify, np.zeros(100))

    def test_classify_ok(self):
        wrapper = KerasModelWrapper(self.test_keras_model)
        wrapper.classify(self.test_sample)
        self.assertTrue(True)

    def test_extract_features_no_array_throws_exception(self):
        wrapper = KerasModelWrapper(self.test_keras_model)
        self.assertRaises(TypeError, wrapper.extract_features, 12)

    def test_extract_features_ok(self):
        wrapper = KerasModelWrapper(self.compliant_object)
        feat_vector = wrapper.extract_features(self.test_sample)
        self.assertTrue((feat_vector == self.test_sample).all())


if __name__ == "__main__":
    unittest.main()
