"""Abstract machine learning model."""
import abc


class Model(metaclass=abc.ABCMeta):
    """Abstract machine learning model wrapper."""

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
            float : the confidence of the malicious class.
        """
        raise NotImplementedError("classify not implemented in abstract class")
