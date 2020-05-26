"""Wrapper for sci-kit learn classifiers.
"""
import os
import joblib
import numpy as np
from wafamole.models import Model
from wafamole.exceptions.models_exceptions import (
    NotSklearnModelError,
    SklearnInternalError,
    ModelNotLoadedError,
)
from wafamole.utils.check import type_check, file_exists


class SklearnModelWrapper(Model):
    """Sci-kit learn classifier wrapper class"""

    def __init__(self, sklearn_classifier=None):
        """Constructs a wrapper around an scikit-learn classifier, or equivalent.
        It must implement predict_proba function.
        
        Arguments:
            sklearn_classifier (sci-kit learn classifier):  scikit-learn classifier or equivalent
        
        Raises:
            NotSklearnModelError: not implement predict_proba
            NotSklearnModelError: not implement fit
        """
        if sklearn_classifier is None:
            self._sklearn_classifier = None
        else:
            if getattr(sklearn_classifier, "predict_proba", None) is None:
                raise NotSklearnModelError(
                    "object does not implement predict_proba function"
                )

            self._sklearn_classifier = sklearn_classifier


    def classify(self, value):
        """It returns the probability of belonging to a particular class.
        It calls the extract_features function on the input value to produce a feature vector.
        
        Arguments:
            value (numpy ndarray) : an input belonging to the input space of the model

        Raises:
            ModelNotLoadedError: calling function without having loaded or passed model as arg

        Returns:
            numpy ndarray : the confidence for each class of the problem.

        """
        if self._sklearn_classifier is None:
            raise ModelNotLoadedError()
        feature_vector = self.extract_features(value)
        try:
            y_pred = self._sklearn_classifier.predict_proba([feature_vector])
            return y_pred
        except Exception as e:
            raise SklearnInternalError("Internal sklearn error.") from e

    def load(self, filepath):
        """Loads a sklearn classifier stored in filepath.
        
        Arguments:
            filepath (string) : The path of the sklearn classifier.

        Raises:
            TypeError: filepath is not string.
            FileNotFoundError: filepath not pointing to any file.
            NotSklearnModelError: model can not be loaded.

        Returns:
            self
        """
        type_check(filepath, str, "filepath")
        file_exists(filepath)
        try:
            self._sklearn_classifier = joblib.load(filepath)
        except Exception as e:
            raise NotSklearnModelError("Error in loading model.") from e
        return self

    def extract_features(self, value: np.ndarray):
        """It returns the input. To modify this behaviour, extend this class and re-define this method.
        
        Arguments:
            value (numpy ndarray) : a sample that belongs to the input space of the model

        Returns:
            the input.
        """
        if type(value) != np.ndarray:
            raise TypeError(f"{type(value)} not an nd array")
        return value
