"""Wrapper for keras classifiers.
"""
from contextlib import redirect_stderr
import os
import numpy as np
from wafamole.models import Model
from wafamole.exceptions.models_exceptions import (
    KerasInternalError,
    NotKerasModelError,
    ModelNotLoadedError,
)
from wafamole.utils.check import type_check, file_exists

with redirect_stderr(open(os.devnull, "w")):
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    import keras


class KerasModelWrapper(Model):
    """Keras model wrapper"""

    def __init__(self, keras_classifier=None):
        if keras_classifier is None:
            self._keras_classifier = None
        else:
            if getattr(keras_classifier, "predict", None) is None:
                raise NotKerasModelError("object does not implement predict function")
            self._keras_classifier = keras_classifier


    def classify(self, value):
        """It returns the probability of belonging to a particular class.
        It calls the extract_features function on the input value to produce a feature vector.
        
        Arguments:
            value  : an input belonging to the input space of the model

        Raises:
            TypeError: value not numpy ndarray
            ModelNotLoadedError: calling function without having loaded or passed model as arg

        Returns:
            the confidence for each class of the problem.
        """
        if type(value) != np.ndarray:
            raise TypeError(f"{type(value)} not an ndarray")
        if self._keras_classifier is None:
            raise ModelNotLoadedError()
        feature_vector = self.extract_features(value)
        try:
            y_pred = self._keras_classifier.predict(np.array([feature_vector]))
            return y_pred
        except Exception as e:
            raise KerasInternalError("Internal keras error.") from e

    def extract_features(self, value):
        """It returns the input. To modify this behaviour, extend this class and re-define this method.
        
        Arguments:
            value (numpy ndarray) : a sample that belongs to the input space of the model

        Returns:
            numpy ndarray : the input.
        """
        if type(value) != np.ndarray:
            raise TypeError(f"{type(value)} not an nd array")
        return value

    def load(self, filepath):
        """Loads a keras classifier stored in filepath.
        
        Arguments:
            filepath (string) : The path of the keras classifier.
        
        Returns:
            self
        Raises:
            TypeError: filepath is not string.
            FileNotFoundError: filepath not pointing to any file.
            NotKerasModelError: model can not be loaded.
        """
        type_check(filepath, str, "filepath")
        file_exists(filepath)

        try:
            self._keras_classifier = keras.models.load_model(filepath)
        except Exception as e:
            raise NotKerasModelError(
                "Can not load keras model. See inner exception for details."
            ) from e
