from wafamole.evasion.engine import CoreEngine
from wafamole.models import Model
from wafamole.payloadfuzzer.sqlfuzzer import SqlFuzzer
import time


class RandomEvasionEngine(CoreEngine):
    def __init__(self, model: Model):
        self._transformations = []
        super(RandomEvasionEngine, self).__init__(model)

    def evaluate(self, payload, max_rounds, round_size, timeout, threshold):
        self._transformations = []

        current_time = time.time()
        print('Start round', time.time())
        while(time.time() < current_time + timeout):
        # for _ in range(max_rounds):
            # print(time.time(), current_time, current_time + timeout)
            conf, payload = self._mutation_round(payload, 1)
            self._transformations.append((conf, payload, time.time()))
        print('End round', time.time())
        return min(self._transformations)

    @property
    def transformations(self):
        return self._transformations
