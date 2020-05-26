from abc import ABCMeta, abstractmethod
from wafamole.payloadfuzzer.sqlfuzzer import SqlFuzzer
from wafamole.models import Model


class CoreEngine(object, metaclass=ABCMeta):

	def __init__(self, model: Model):
		self._model = model

	def _mutation_round(self, payload, round_size):
		fuzzer = SqlFuzzer(payload)

		# Some mutations do not apply to some payloads
		# This removes duplicate payloads
		payloads = {fuzzer.fuzz() for _ in range(round_size)}
		results = map(self._model.classify, payloads)
		confidence, payload = min(zip(results, payloads))
		return confidence, payload

	@abstractmethod
	def evaluate(self, payload, max_rounds, round_size, timeout, threshold):
		"""It tries to produce a payloads that should be classified as a benign payload.

		Arguments:
			payload (str) : the initial payload
			max_rounds (int) : maximum number of mutation rounds
			round_size (int) : how many mutation for each round
			timeout (int) : number of seconds before the timeout
			threshold (float) : default 0.5, customizable for different results

		Returns:
			float, str : minimum confidence and correspondent payload that achieve that score
		"""
		raise NotImplementedError("")