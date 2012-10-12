import random


class GeneticAlgorithm:

    def __call__(self, generations=20, survived_count=20, hybrid_count=10, mutant_count=10):

        population_count = survived_count + hybrid_count + mutant_count

        self._individuals = [self._spawn() for _ in xrange(population_count)]

        for _ in xrange(generations):

            # Sort from the fittest to the least fit
            self._individuals.sort(key=self._fit, reverse=True)

            survived = self._individuals[:survived_count]
            hybrids = map(self._cross, random.sample(survived, hybrid_count), random.sample(survived, hybrid_count))
            mutants = map(self._mutate, random.sample(survived, mutant_count))

            self._individuals = survived + hybrids + mutants

        return survived[0]

    def _fit(self, individual):
        raise NotImplementedError()

    def _spawn(self):
        raise NotImplementedError()

    def _cross(self, first, second):
        raise NotImplementedError()

    def _mutate(self, individual):
        raise NotImplementedError()
