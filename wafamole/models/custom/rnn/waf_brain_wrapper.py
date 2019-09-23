from wafamole.models.custom.rnn.waf_brain import process_payload
from wafamole.models import KerasModelWrapper
from wafamole.utils.check import type_check, file_exists


class WafBrainWrapper(KerasModelWrapper):
    """WafBrain wrapper"""

    def __init__(self, filepath: str):
        """Constructs model by loading pretrained net.
        
        Arguments:
            filepath (str) : the path to the pretrained h5 net

        Raises:
        TypeError: filepath not  string
        FileNotFoundError: filepath not pointing to anything
        NotKerasModelError: filepath not pointing to h5 keras model
        """
        type_check(filepath, str, "filepath")
        file_exists(filepath)
        self.load(filepath)
        super(WafBrainWrapper, self).__init__(self._keras_classifier)

    def extract_features(self, value: str):
        """No feature extraction
        
        Arguments:
            value (str) : input query string
        
        Raises:
        TypeError: value is not string

        Returns:
            str : the input value
        """
        type_check(value, str, "value")
        return value

    def classify(self, value: str):
        """Produce probability of being sql injection.
        
        Arguments:
            value (str) : input query
        
        Raises:
        TypeError: value is not string

        Returns:
           float : probability of being a sql injection
        """
        type_check(value, str, "value")
        malicious = process_payload(self._keras_classifier, "", [value])["score"]
        return malicious
