from wafamole.tokenizer import Tokenizer
from wafamole.models import SklearnModelWrapper
from wafamole.utils.check import type_check


class TokenClassifierWrapper(SklearnModelWrapper):
    def extract_features(self, value: str):
        type_check(value, str, "value")
        tokenizer = Tokenizer()
        feature_vector = tokenizer.produce_feat_vector(value)
        return feature_vector

    def classify(self, value):
        return super(TokenClassifierWrapper, self).classify(value)[0, 1]
