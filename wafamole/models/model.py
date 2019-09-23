"""Abstract machine learning model."""
import abc


class Model(metaclass=abc.ABCMeta):
    """Abstract machine learning model wrapper."""

    @abc.abstractmethod
    def fit(self, X, Y):
        """Fit the wrapped model by feeding it with X and Y.

        Arguments:
            X (list of data samples) : the training data
            Y (list of classes) : the training labels

        Returns:
            self

        Raises:
            NotImplementedError: this method needs to be implemented
        """
        raise NotImplementedError("fit not implemented in abstract class")

    @abc.abstractmethod
    def extract_features(self, value: object):
        """It extract a feature vector from the input object.

        Arguments:
            value (object) : An input point that belongs to the input space of the wrapped model.

        Returns:
            feature_vector (numpy ndarray) : array containing the feature vector of the input value.

        Raises:
            NotImplementedError: this method needs to be implemented
        """
        raise NotImplementedError("extract_features not implemented in abstract class")

    @abc.abstractmethod
    def classify(self, value: object):
        """It returns the probability of belonging to a particular class.
        It calls the extract_features function on the input value to produce a feature vector.
        
        Arguments:
            value (object) : Input value

        Returns:
            numpy ndarray : the confidence for each class of the classifier.
            If binary classifications, it returns a [1,2] matrix, where the first entry is probability of being 0 and
            the second entry is the probability of being 1 (namely, (1-p, p))
        """
        raise NotImplementedError("classify not implemented in abstract class")
