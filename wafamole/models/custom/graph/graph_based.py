from wafamole.models.custom.graph.sqligot import SQLiGoT
from wafamole.models import SklearnModelWrapper
from wafamole.utils.check import type_check
from wafamole.exceptions.models_exceptions import (
    ModelNotLoadedError,
    SklearnInternalError,
)


class SQLiGoTWrapper(SklearnModelWrapper):
    """SQLiGoT wrapper"""

    def __init__(
        self, sqligot_classifier: SQLiGoT = None, undirected=True, proportional=True
    ):
        """Constructs the wrapper.
        
        Arguments:

        Keyword Arguments:
            sqligot_classifier (SQLiGoT) : SQLiGoT object (default: None)
            undirected (bool) : set undirection for feature extraction (default: (True))
            proportional (bool) : set weights for edges in graph (default: (True))

        Raises:
            TypeError: wrong input types
        
        Returns:
            SQLiGoTWrapper : the object
        """
        if sqligot_classifier is not None:
            type_check(sqligot_classifier, SQLiGoT, "sqligot_classifier")
        type_check(undirected, bool, "undirected")
        type_check(proportional, bool, "proportional")

        self._undirected = undirected
        self._proportional = proportional
        return super(SQLiGoTWrapper, self).__init__(sqligot_classifier)

    def extract_features(self, value: str):
        """Extract feature vector using SQLiGoT extractor.
        
        Arguments:
            value (str) : the input SQL query.

        Raises:
            TypeError: value is not string
            ModelNotLoadedError: calling function without having loaded or passed model as arg

        Returns:
            numpy ndarray : the feature vector
        """
        if self._sklearn_classifier is None:
            raise ModelNotLoadedError()
        type_check(value, str, "value")
        query = self._sklearn_classifier.preprocess_single_query(
            value, undirected=self._undirected, proportional=self._proportional
        )

        return query

    def classify(self, value):
        """Computes the probability of being a sql injection.

        Arguments:
            value: the input query

        Raises:
            ModuleNotLoadedError: calling function without having loaded or passed model as arg
            SklearnInternalError: internal sklearn exception has been thrown

        Returns:
            probability of being a sql injection.
        """
        if self._sklearn_classifier is None:
            raise ModelNotLoadedError()
        feature_vector = self.extract_features(value)
        if feature_vector is None:
            return 1
        try:
            y_pred = self._sklearn_classifier.predict_proba([feature_vector])
            return y_pred[0, 1]
        except Exception as e:
            raise SklearnInternalError("Internal sklearn error.") from e
        return super(SQLiGoTWrapper, self).classify(value)[0, 1]
